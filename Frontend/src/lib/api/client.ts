/**
 * Typed fetch wrapper for the Fast Accounts backend.
 * Handles JWT injection, refresh-on-401, and JSON (camelCase) marshalling.
 */
import { getApiOrigin, resolveApiUrl } from "@/lib/api/base-url";
import {
  clearEtagCache,
  clearEtagCacheForCompany,
  etagCacheKey,
  getEtagEntry,
  setEtagEntry,
} from "@/lib/api/etag-store";
import { getCurrentCompanyId, getTokens, setTokens, clearTokens } from "@/lib/auth/storage";

export class ApiError extends Error {
  status: number;
  detail: unknown;
  constructor(status: number, detail: unknown, message?: string) {
    super(message ?? `API ${status}`);
    this.status = status;
    this.detail = detail;
  }
}

type Method = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

interface RequestOptions {
  method?: Method;
  body?: unknown;
  query?: Record<string, string | number | boolean | undefined>;
  signal?: AbortSignal;
  /** Skip the access-token Authorization header (auth endpoints). */
  anonymous?: boolean;
}

function buildUrl(path: string, query?: RequestOptions["query"]): string {
  const url = new URL(resolveApiUrl(path));
  if (query) {
    for (const [k, v] of Object.entries(query)) {
      if (v !== undefined) url.searchParams.set(k, String(v));
    }
  }
  return url.toString();
}

async function refreshAccessToken(): Promise<boolean> {
  const tokens = getTokens();
  if (!tokens?.refreshToken) return false;
  try {
    const res = await fetch(resolveApiUrl("/api/v1/auth/refresh"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        refreshToken: tokens.refreshToken,
        companyId: getCurrentCompanyId() ?? undefined,
      }),
    });
    if (!res.ok) return false;
    const text = await res.text();
    let data: {
      accessToken: string;
      refreshToken: string;
      tokenType: string;
    };
    try {
      data = JSON.parse(text) as typeof data;
    } catch {
      return false;
    }
    setTokens(
      {
        accessToken: data.accessToken,
        refreshToken: data.refreshToken,
      },
      { syncCompanyFromToken: false },
    );
    return true;
  } catch {
    return false;
  }
}

async function performFetch(
  url: string,
  init: RequestInit,
  anonymous: boolean,
): Promise<Response> {
  let res: Response;
  try {
    res = await fetch(url, init);
  } catch (err) {
    const hint =
      err instanceof TypeError
        ? `Cannot reach the API at ${getApiOrigin()}. Check that the backend is running on port 8000 (dev proxy) or set NEXT_PUBLIC_API_BASE_URL.`
        : undefined;
    throw new Error(hint ?? (err instanceof Error ? err.message : "Network request failed"));
  }

  if (res.status === 401 && !anonymous) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      const headers = new Headers(init.headers);
      const tokens = getTokens();
      if (tokens?.accessToken) headers.set("Authorization", `Bearer ${tokens.accessToken}`);
      res = await fetch(url, { ...init, headers });
    } else {
      clearTokens();
    }
  }
  return res;
}

function parseResponse<T>(res: Response, text: string): T {
  if (res.status === 204) return undefined as T;
  const parsed = text ? safeJson(text) : undefined;
  if (!res.ok) {
    throw new ApiError(res.status, parsed, extractMessage(parsed) ?? res.statusText);
  }
  return parsed as T;
}

export async function apiFetch<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { method = "GET", body, query, signal, anonymous } = options;
  const headers: Record<string, string> = { Accept: "application/json" };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (!anonymous) {
    const tokens = getTokens();
    if (tokens?.accessToken) headers.Authorization = `Bearer ${tokens.accessToken}`;
  }

  const init: RequestInit = {
    method,
    headers,
    signal,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  };

  const res = await performFetch(buildUrl(path, query), init, !!anonymous);
  const text = await res.text();
  return parseResponse<T>(res, text);
}

/**
 * GET with If-None-Match / ETag support for reference endpoints.
 * Returns cached body on 304 without re-parsing JSON.
 */
export async function apiFetchCached<T>(
  path: string,
  options: Omit<RequestOptions, "method" | "body"> = {},
): Promise<T> {
  const { query, signal, anonymous } = options;
  const url = buildUrl(path, query);
  const companyId = getCurrentCompanyId();
  const cacheKey = etagCacheKey("GET", url, companyId);
  const cached = getEtagEntry(cacheKey);

  const headers: Record<string, string> = { Accept: "application/json" };
  if (!anonymous) {
    const tokens = getTokens();
    if (tokens?.accessToken) headers.Authorization = `Bearer ${tokens.accessToken}`;
  }
  if (cached?.etag) headers["If-None-Match"] = `"${cached.etag}"`;

  const init: RequestInit = { method: "GET", headers, signal };
  const res = await performFetch(url, init, !!anonymous);

  if (res.status === 304 && cached) {
    return cached.body as T;
  }

  const text = await res.text();
  const parsed = parseResponse<T>(res, text);
  const etagHeader = res.headers.get("ETag");
  if (etagHeader) {
    const etag = etagHeader.replace(/^"|"$/g, "");
    setEtagEntry(cacheKey, etag, parsed);
  }
  return parsed;
}

export { clearEtagCache, clearEtagCacheForCompany };

function safeJson(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    const trimmed = text.trimStart();
    if (trimmed.startsWith("<")) {
      throw new Error(
        "API returned HTML instead of JSON. Check that the backend is running on port 8000 and restart it if you recently pulled API changes.",
      );
    }
    return text;
  }
}

function extractMessage(payload: unknown): string | undefined {
  if (!payload || typeof payload !== "object") return undefined;
  const obj = payload as Record<string, unknown>;
  if (typeof obj.detail === "string") return obj.detail;
  if (typeof obj.message === "string") return obj.message;
  const detail = obj.detail;
  if (detail && typeof detail === "object") {
    const nested = detail as Record<string, unknown>;
    if (typeof nested.message === "string") return nested.message;
  }
  return undefined;
}
