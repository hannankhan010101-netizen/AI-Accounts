import { keepPreviousData, type UseQueryOptions } from "@tanstack/react-query";

import { queryDefaults } from "@/lib/query/defaults";

/** Merge reference-data cache defaults (COA, settings, permissions catalog). */
export function referenceQueryOptions<
  TQueryFnData = unknown,
  TError = Error,
  TData = TQueryFnData,
  TQueryKey extends readonly unknown[] = readonly unknown[],
>(
  options: UseQueryOptions<TQueryFnData, TError, TData, TQueryKey>,
): UseQueryOptions<TQueryFnData, TError, TData, TQueryKey> {
  return { ...queryDefaults.reference, ...options };
}

/** Merge list-page defaults (inherits global staleTime when omitted). */
export function listQueryOptions<
  TQueryFnData = unknown,
  TError = Error,
  TData = TQueryFnData,
  TQueryKey extends readonly unknown[] = readonly unknown[],
>(
  options: UseQueryOptions<TQueryFnData, TError, TData, TQueryKey>,
): UseQueryOptions<TQueryFnData, TError, TData, TQueryKey> {
  return { ...queryDefaults.list, ...options };
}

/** Paginated lists — keeps prior page visible while fetching the next page. */
export function paginatedListQueryOptions<
  TQueryFnData = unknown,
  TError = Error,
  TData = TQueryFnData,
  TQueryKey extends readonly unknown[] = readonly unknown[],
>(
  options: UseQueryOptions<TQueryFnData, TError, TData, TQueryKey>,
): UseQueryOptions<TQueryFnData, TError, TData, TQueryKey> {
  return {
    ...queryDefaults.list,
    placeholderData: keepPreviousData,
    ...options,
  };
}

/** Merge document/detail defaults — refetch on mount after edits. */
export function detailQueryOptions<
  TQueryFnData = unknown,
  TError = Error,
  TData = TQueryFnData,
  TQueryKey extends readonly unknown[] = readonly unknown[],
>(
  options: UseQueryOptions<TQueryFnData, TError, TData, TQueryKey>,
): UseQueryOptions<TQueryFnData, TError, TData, TQueryKey> {
  return { ...queryDefaults.detail, ...options };
}

/** Financial / catalog reports — longer stale window, keep prior params visible. */
export function reportQueryOptions<
  TQueryFnData = unknown,
  TError = Error,
  TData = TQueryFnData,
  TQueryKey extends readonly unknown[] = readonly unknown[],
>(
  options: UseQueryOptions<TQueryFnData, TError, TData, TQueryKey>,
): UseQueryOptions<TQueryFnData, TError, TData, TQueryKey> {
  return {
    ...queryDefaults.report,
    placeholderData: keepPreviousData,
    ...options,
  };
}
