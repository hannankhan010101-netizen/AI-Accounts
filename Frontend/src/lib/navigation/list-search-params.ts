/** Standard list URL params: `?q=…&page=2` (bookmarkable, shareable). */

export const LIST_Q_PARAM = "q";
export const LIST_PAGE_PARAM = "page";
export const LIST_STATUS_PARAM = "status";

export function parseListPage(searchParams: URLSearchParams, fallback = 1): number {
  const p = parseInt(searchParams.get(LIST_PAGE_PARAM) ?? String(fallback), 10);
  return Number.isFinite(p) && p > 0 ? p : fallback;
}

export function parseListQuery(searchParams: URLSearchParams): string {
  return searchParams.get(LIST_Q_PARAM) ?? "";
}

export function parseListStatus(searchParams: URLSearchParams): "" | "active" | "inactive" {
  const s = searchParams.get(LIST_STATUS_PARAM);
  if (s === "active" || s === "inactive") return s;
  return "";
}

/**
 * Merge list params into a copy of `current`. Other query keys (e.g. userId) are preserved.
 */
export function patchListSearchParams(
  current: URLSearchParams,
  patch: {
    q?: string;
    page?: number;
    status?: "" | "active" | "inactive";
  },
): URLSearchParams {
  const next = new URLSearchParams(current.toString());

  if (patch.q !== undefined) {
    const trimmed = patch.q.trim();
    if (trimmed) next.set(LIST_Q_PARAM, trimmed);
    else next.delete(LIST_Q_PARAM);
    next.delete(LIST_PAGE_PARAM);
  }

  if (patch.page !== undefined) {
    if (patch.page > 1) next.set(LIST_PAGE_PARAM, String(patch.page));
    else next.delete(LIST_PAGE_PARAM);
  }

  if (patch.status !== undefined) {
    if (patch.status) next.set(LIST_STATUS_PARAM, patch.status);
    else next.delete(LIST_STATUS_PARAM);
    if (patch.q === undefined) next.delete(LIST_PAGE_PARAM);
  }

  return next;
}

export function listSearchHref(pathname: string, params: URLSearchParams): string {
  const qs = params.toString();
  return qs ? `${pathname}?${qs}` : pathname;
}
