/** Session-scoped form drafts (survives refresh, cleared on successful save). */

export function formDraftKey(companyId: string, scope: string): string {
  return `draft:${companyId}:${scope}`;
}

export function readFormDraft<T>(key: string): T | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = sessionStorage.getItem(key);
    if (!raw) return null;
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

export function writeFormDraft<T>(key: string, value: T): void {
  try {
    sessionStorage.setItem(key, JSON.stringify(value));
  } catch {
    /* quota exceeded — ignore */
  }
}

export function clearFormDraft(key: string): void {
  sessionStorage.removeItem(key);
}

export function draftsEqual(a: unknown, b: unknown): boolean {
  try {
    return JSON.stringify(a) === JSON.stringify(b);
  } catch {
    return false;
  }
}
