/** Shared client-side search helpers for list pages. */

export function matchText(parts: (string | null | undefined | unknown)[], query: string): boolean {
  const hay = parts
    .filter((p) => p != null && p !== "")
    .map((p) => String(p))
    .join(" ")
    .toLowerCase();
  return hay.includes(query);
}
