/**
 * Enterprise AI assistant API — SSE streaming via FastAPI.
 */
import { getApiOrigin, resolveApiUrl } from "@/lib/api/base-url";
import { isAbortError } from "@/lib/api/abort-error";
import { getCurrentCompanyId, getTokens } from "@/lib/auth/storage";
import type { AiSuggestion } from "@/lib/tour/types";

function path(suffix: string): string {
  const id = getCurrentCompanyId();
  if (!id) throw new Error("No company selected");
  return `/api/v1/companies/${id}${suffix}`;
}

export type AssistantStreamEvent =
  | { type: "thread"; threadId: string }
  | { type: "token"; content: string }
  | {
      type: "tool_call";
      threadId: string;
      toolCallId: string;
      name: string;
      arguments: Record<string, unknown>;
    }
  | { type: "done"; threadId?: string; engine?: string }
  | {
      type: "error";
      message: string;
      code?: string;
      retryable?: boolean;
    };

export type AssistantMessage = {
  id?: string;
  role: "user" | "assistant" | "tool";
  content: string;
  toolName?: string | null;
  toolPayload?: unknown;
  createdAt?: string | null;
};

async function refreshAccessToken(): Promise<boolean> {
  const tokens = getTokens();
  if (!tokens?.refreshToken) return false;
  try {
    const res = await fetch(resolveApiUrl("/api/v1/auth/refresh"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refreshToken: tokens.refreshToken }),
    });
    if (!res.ok) return false;
    const data = (await res.json()) as {
      accessToken: string;
      refreshToken: string;
    };
    const { setTokens } = await import("@/lib/auth/storage");
    setTokens({
      accessToken: data.accessToken,
      refreshToken: data.refreshToken,
    });
    return true;
  } catch {
    return false;
  }
}

function authHeaders(): Record<string, string> {
  const tokens = getTokens();
  const h: Record<string, string> = { Accept: "text/event-stream" };
  if (tokens?.accessToken) h.Authorization = `Bearer ${tokens.accessToken}`;
  return h;
}

async function fetchStream(
  url: string,
  init: RequestInit,
  onEvent: (event: AssistantStreamEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  let res: Response;
  try {
    res = await fetch(url, { ...init, signal, headers: { ...authHeaders(), ...init.headers } });
  } catch (err) {
    if (isAbortError(err) || signal?.aborted) return;
    const hint =
      err instanceof TypeError
        ? `Cannot reach the API at ${getApiOrigin()}. Ensure the backend is running on port 8000 (dev proxy) or set NEXT_PUBLIC_API_BASE_URL.`
        : undefined;
    onEvent({ type: "error", message: hint ?? (err instanceof Error ? err.message : "Failed to fetch") });
    return;
  }
  if (res.status === 401) {
    const ok = await refreshAccessToken();
    if (ok) {
      res = await fetch(url, { ...init, signal, headers: { ...authHeaders(), ...init.headers } });
    }
  }
  if (!res.ok) {
    const text = await res.text();
    let message = `Assistant request failed (${res.status})`;
    try {
      const j = JSON.parse(text) as { detail?: string | { message?: string } };
      if (typeof j.detail === "string") message = j.detail;
      else if (j.detail && typeof j.detail === "object" && "message" in j.detail) {
        message = String((j.detail as { message?: string }).message);
      }
    } catch {
      /* ignore */
    }
    onEvent({ type: "error", message });
    return;
  }

  const reader = res.body?.getReader();
  if (!reader) {
    onEvent({ type: "error", message: "No response body" });
    return;
  }

  const decoder = new TextDecoder();
  let buffer = "";

  const parseBuffer = (chunk: string) => {
    const parts = chunk.split("\n\n");
    const remainder = parts.pop() ?? "";
    for (const part of parts) {
      for (const line of part.split("\n")) {
        if (!line.startsWith("data: ")) continue;
        try {
          const payload = JSON.parse(line.slice(6)) as AssistantStreamEvent;
          onEvent(payload);
        } catch {
          /* skip malformed */
        }
      }
    }
    return remainder;
  };

  try {
    while (true) {
      if (signal?.aborted) return;
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      buffer = parseBuffer(buffer);
    }
    if (buffer.trim()) {
      parseBuffer(`${buffer}\n\n`);
    }
  } catch (err) {
    if (isAbortError(err) || signal?.aborted) return;
    throw err;
  }
}

export const assistantApi = {
  streamChat: (
    body: {
      message: string;
      pathname: string;
      threadId?: string | null;
      locale?: string;
      mode?: string;
      entityContext?: Record<string, unknown>;
    },
    onEvent: (event: AssistantStreamEvent) => void,
    signal?: AbortSignal,
  ) =>
    fetchStream(
      resolveApiUrl(path("/me/assistant/chat/stream")),
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      },
      onEvent,
      signal,
    ),

  postToolResult: (
    body: { threadId: string; toolCallId: string; result: Record<string, unknown> },
    onEvent: (event: AssistantStreamEvent) => void,
    signal?: AbortSignal,
  ) =>
    fetchStream(
      resolveApiUrl(path("/me/assistant/chat/tool-result")),
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      },
      onEvent,
      signal,
    ),

  getThreadMessages: (threadId: string) =>
    import("./client").then(({ apiFetch }) =>
      apiFetch<{ result: { threadId: string; messages: AssistantMessage[] } }>(
        path(`/me/assistant/threads/${threadId}/messages`),
      ),
    ),

  deleteThread: (threadId: string) =>
    import("./client").then(({ apiFetch }) =>
      apiFetch<{ result: { deleted: boolean } }>(
        path(`/me/assistant/threads/${threadId}`),
        { method: "DELETE" },
      ),
    ),

  getSuggestions: (pathname: string) =>
    import("./client").then(({ apiFetch }) =>
      apiFetch<{
        result: {
          suggestions: AiSuggestion[];
          pathname: string;
          engine: "rules" | "llm" | "groq";
        };
      }>(path("/me/assistant/suggestions"), { query: { pathname } }),
    ),
};
