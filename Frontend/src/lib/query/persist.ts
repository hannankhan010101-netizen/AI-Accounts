/**
 * sessionStorage persistence for reference + report React Query tiers.
 */
import { defaultShouldDehydrateQuery, type Query } from "@tanstack/react-query";
import { createSyncStoragePersister } from "@tanstack/query-sync-storage-persister";

import { STALE_REFERENCE_MS, STALE_REPORT_MS } from "@/lib/query/defaults";

export const QUERY_PERSIST_KEY = "fa-rq-v1";

export function createSessionQueryPersister() {
  if (typeof window === "undefined") return null;
  return createSyncStoragePersister({
    storage: window.sessionStorage,
    key: QUERY_PERSIST_KEY,
  });
}

/** Only persist tenant-scoped reference (5m) and report (2m) queries. */
export function shouldPersistTenantQuery(query: Query): boolean {
  if (!defaultShouldDehydrateQuery(query)) return false;

  const key = query.queryKey;
  if (!Array.isArray(key) || key[0] !== "tenant" || !key[1]) return false;

  const staleTime =
    (query.options as { staleTime?: number | typeof Infinity }).staleTime ?? 0;
  if (staleTime === 0) return false;

  return staleTime === STALE_REFERENCE_MS || staleTime === STALE_REPORT_MS;
}
