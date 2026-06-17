/**
 * API base URL. In the browser during local dev, defaults to same-origin so
 * Next.js rewrites proxy /api/v1/* to the backend (no CORS preflight failures).
 */
export function getApiBaseUrl(): string {
  const configured = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
  if (configured) return configured.replace(/\/$/, "");
  if (typeof window !== "undefined") return "";
  return "http://localhost:8000";
}

/** Origin used to resolve relative API paths (never pass a bare path to `new URL(path)`). */
export function getApiOrigin(): string {
  const base = getApiBaseUrl();
  if (base) return base;
  if (typeof window !== "undefined") return window.location.origin;
  return "http://localhost:8000";
}

/** Build an absolute URL for fetch / URL APIs from an API path like `/api/v1/...`. */
export function resolveApiUrl(path: string): string {
  if (path.startsWith("http")) return path;
  return new URL(path, getApiOrigin()).toString();
}
