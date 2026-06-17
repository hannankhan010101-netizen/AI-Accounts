/**
 * Tenant-scoped React Query helpers.
 * Keys include companyId so data refetches automatically when the active company changes.
 */
"use client";

import {
  useQuery,
  useQueryClient,
  keepPreviousData,
  type QueryClient,
  type QueryKey,
  type UseQueryOptions,
  type UseQueryResult,
} from "@tanstack/react-query";

import { useCompany } from "@/lib/auth/company-context";
import { setCurrentCompanyId } from "@/lib/auth/storage";
import { queryDefaults } from "@/lib/query/defaults";

/** Build a cache key scoped to the active company. */
export function tenantQueryKey(companyId: string | null | undefined, ...parts: unknown[]): QueryKey {
  return ["tenant", companyId ?? "", ...parts];
}

export function useTenantQueryKey(...parts: unknown[]): QueryKey {
  const { companyId } = useCompany();
  return tenantQueryKey(companyId, ...parts);
}

/** Call after create/update/delete so list pages show fresh data. */
export function invalidateTenantQueries(queryClient: QueryClient, ...keyParts: unknown[]) {
  if (keyParts.length === 0) {
    return queryClient.invalidateQueries({ queryKey: ["tenant"] });
  }
  return queryClient.invalidateQueries({
    predicate: (q) =>
      Array.isArray(q.queryKey) &&
      q.queryKey[0] === "tenant" &&
      keyParts.every((part, i) => q.queryKey[i + 2] === part),
  });
}

export function prefetchTenantQuery<T>(
  queryClient: QueryClient,
  companyId: string,
  keyParts: unknown[],
  queryFn: () => Promise<T>,
  options?: Omit<UseQueryOptions<T, Error, T, QueryKey>, "queryKey" | "queryFn">,
) {
  return queryClient.prefetchQuery({
    queryKey: tenantQueryKey(companyId, ...keyParts),
    queryFn: () => {
      setCurrentCompanyId(companyId);
      return queryFn();
    },
    ...options,
  });
}

export function useTenantQueryClient() {
  const queryClient = useQueryClient();
  const { companyId } = useCompany();

  return {
    companyId,
    invalidateTenant: (...keyParts: unknown[]) => invalidateTenantQueries(queryClient, ...keyParts),
    prefetchTenant: <T>(
      keyParts: unknown[],
      queryFn: () => Promise<T>,
      options?: Omit<UseQueryOptions<T, Error, T, QueryKey>, "queryKey" | "queryFn">,
    ) => {
      if (!companyId) return Promise.resolve();
      return prefetchTenantQuery(queryClient, companyId, keyParts, queryFn, options);
    },
  };
}

type TenantQueryExtras<T> = Omit<
  UseQueryOptions<T, Error, T, QueryKey>,
  "queryKey" | "queryFn" | "enabled"
> & { enabled?: boolean };

export function useTenantQuery<T>(
  keyParts: unknown[],
  queryFn: () => Promise<T>,
  options?: TenantQueryExtras<T>,
): UseQueryResult<T, Error> {
  const { companyId, isLoading: companyLoading } = useCompany();
  const queryKey = tenantQueryKey(companyId, ...keyParts);
  return useQuery({
    queryKey,
    queryFn: () => {
      if (!companyId) throw new Error("No company selected");
      setCurrentCompanyId(companyId);
      return queryFn();
    },
    enabled: !companyLoading && !!companyId && (options?.enabled ?? true),
    ...options,
  }) as UseQueryResult<T, Error>;
}

export function useTenantReferenceQuery<T>(
  keyParts: unknown[],
  queryFn: () => Promise<T>,
  options?: TenantQueryExtras<T>,
): UseQueryResult<T, Error> {
  return useTenantQuery(keyParts, queryFn, { ...queryDefaults.reference, ...options });
}

export function useTenantListQuery<T>(
  keyParts: unknown[],
  queryFn: () => Promise<T>,
  options?: TenantQueryExtras<T>,
): UseQueryResult<T, Error> {
  return useTenantQuery(keyParts, queryFn, { ...queryDefaults.list, ...options });
}

export function useTenantDetailQuery<T>(
  keyParts: unknown[],
  queryFn: () => Promise<T>,
  options?: TenantQueryExtras<T>,
): UseQueryResult<T, Error> {
  return useTenantQuery(keyParts, queryFn, { ...queryDefaults.detail, ...options });
}

export function useTenantReportQuery<T>(
  keyParts: unknown[],
  queryFn: () => Promise<T>,
  options?: TenantQueryExtras<T>,
): UseQueryResult<T, Error> {
  return useTenantQuery(keyParts, queryFn, {
    ...queryDefaults.report,
    placeholderData: keepPreviousData,
    ...options,
  });
}
