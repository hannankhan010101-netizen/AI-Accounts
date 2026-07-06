/**
 * Prefetch hot shell reference data into React Query after company bootstrap.
 */
import type { QueryClient } from "@tanstack/react-query";

import { clearEtagCacheForCompany } from "@/lib/api/client";
import {
  appSettingsApi,
  dashboardApi,
  ledgerApi,
  rbacApi,
  reportsApi,
} from "@/lib/api/tenant";
import { prefetchTenantQuery } from "@/lib/api/tenant-query";
import { queryDefaults } from "@/lib/query/defaults";
import { setCurrentCompanyId } from "@/lib/auth/storage";

async function runWarmupBatch(
  queryClient: QueryClient,
  companyId: string,
  batch: Array<{
    key: unknown[];
    queryFn: () => Promise<unknown>;
    tier?: keyof typeof queryDefaults;
  }>,
): Promise<void> {
  await Promise.allSettled(
    batch.map(({ key, queryFn, tier = "reference" }) =>
      prefetchTenantQuery(queryClient, companyId, key, queryFn, queryDefaults[tier]),
    ),
  );
}

export async function warmupShellCache(
  queryClient: QueryClient,
  companyId: string,
): Promise<void> {
  setCurrentCompanyId(companyId);

  // Wave 1 gates the shell: the sidebar/menu and permission checks need these
  // before the app frame can render, so they get their own round-trip first.
  await runWarmupBatch(queryClient, companyId, [
    { key: ["content-menu"], queryFn: () => appSettingsApi.getMenuLayout() },
    { key: ["my-permissions"], queryFn: () => rbacApi.getMyPermissions() },
  ]);

  // Wave 2: everything the landing dashboard needs, all in parallel. These have
  // no dependency on each other, so there is no reason to stage them — the
  // heavy command-center aggregation starts on the same round-trip as the rest.
  await runWarmupBatch(queryClient, companyId, [
    { key: ["coa-tree"], queryFn: () => ledgerApi.getCoaTree() },
    {
      key: ["report-definitions", "catalog"],
      queryFn: () => reportsApi.listDefinitions(),
    },
    {
      key: ["dashboard-settings"],
      queryFn: () => appSettingsApi.getDashboardSettings(),
    },
    {
      key: ["dashboard-layout"],
      queryFn: () => dashboardApi.getLayout(),
    },
    {
      key: ["command-center", "fy", "month"],
      queryFn: () => dashboardApi.commandCenter({ period: "fy", salesGranularity: "month" }),
      tier: "report",
    },
  ]);
}

export function resetShellHttpCache(companyId: string | null): void {
  clearEtagCacheForCompany(companyId);
}
