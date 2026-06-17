/** Unwrap extended report API payloads — backend returns `{ rows, totals }`. */

export function unwrapExtendedReportRows(
  payload: Record<string, unknown>[] | { rows?: Record<string, unknown>[] } | undefined,
): Record<string, unknown>[] {
  if (!payload) return [];
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload.rows)) return payload.rows;
  return [];
}
