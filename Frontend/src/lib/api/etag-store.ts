/** In-memory ETag cache for conditional GET (browser session RAM). */

type EtagEntry = { etag: string; body: unknown };

const store = new Map<string, EtagEntry>();

export function etagCacheKey(method: string, url: string, companyId: string | null): string {
  return `${method}:${url}:${companyId ?? ""}`;
}

export function getEtagEntry(key: string): EtagEntry | undefined {
  return store.get(key);
}

export function setEtagEntry(key: string, etag: string, body: unknown): void {
  store.set(key, { etag, body });
}

export function deleteEtagEntry(key: string): void {
  store.delete(key);
}

/** Clear all entries, or those whose cache key contains `pathFragment`. */
export function clearEtagCache(pathFragment?: string): void {
  if (!pathFragment) {
    store.clear();
    return;
  }
  for (const key of store.keys()) {
    if (key.includes(pathFragment)) store.delete(key);
  }
}

export function clearEtagCacheForCompany(companyId: string | null): void {
  if (!companyId) {
    store.clear();
    return;
  }
  const suffix = `:${companyId}`;
  for (const key of [...store.keys()]) {
    if (key.endsWith(suffix)) store.delete(key);
  }
}
