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

  await runWarmupBatch(queryClient, companyId, [
    { key: ["content-menu"], queryFn: () => appSettingsApi.getMenuLayout() },
    { key: ["my-permissions"], queryFn: () => rbacApi.getMyPermissions() },
  ]);

  await runWarmupBatch(queryClient, companyId, [
    { key: ["coa-tree"], queryFn: () => ledgerApi.getCoaTree() },
    {
      key: ["report-definitions", "catalog"],
      queryFn: () => reportsApi.listDefinitions(),
    },
  ]);

  await runWarmupBatch(queryClient, companyId, [
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
