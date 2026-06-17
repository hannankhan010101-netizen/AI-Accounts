/** Shared TanStack Query defaults by data class. */

/** Reference / settings data that changes rarely */
export const STALE_REFERENCE_MS = 5 * 60 * 1000;
export const GC_REFERENCE_MS = 30 * 60 * 1000;

/** Standard list pages */
export const STALE_LIST_MS = 30 * 1000;
export const GC_LIST_MS = 10 * 60 * 1000;

/** Document detail — refetch on mount after edits */
export const STALE_DETAIL_MS = 0;
export const GC_DETAIL_MS = 5 * 60 * 1000;

/** Financial reports — aligns with backend Redis report cache TTL */
export const STALE_REPORT_MS = 2 * 60 * 1000;
export const GC_REPORT_MS = 15 * 60 * 1000;

/** Global QueryClient default gcTime */
export const GC_DEFAULT_MS = 10 * 60 * 1000;

export const queryDefaults = {
  reference: {
    staleTime: STALE_REFERENCE_MS,
    gcTime: GC_REFERENCE_MS,
    refetchOnWindowFocus: false,
  },
  list: {
    staleTime: STALE_LIST_MS,
    gcTime: GC_LIST_MS,
    refetchOnWindowFocus: true,
  },
  detail: {
    staleTime: STALE_DETAIL_MS,
    gcTime: GC_DETAIL_MS,
    refetchOnWindowFocus: true,
  },
  report: {
    staleTime: STALE_REPORT_MS,
    gcTime: GC_REPORT_MS,
    refetchOnWindowFocus: false,
  },
} as const;
