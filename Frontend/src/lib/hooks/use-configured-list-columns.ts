"use client";
import { useTenantReferenceQuery } from "@/lib/api/tenant-query";

import { useMemo } from "react";


import type { GridColumn } from "@/components/ui/enterprise-grid";
import { applyListingLayout } from "@/lib/grid/apply-listing-layout";
import { appSettingsApi } from "@/lib/api/tenant";


/** Merge saved Content Settings layout with a list page column definition. */
export function useConfiguredListColumns<Row extends Record<string, unknown>>(
  listingId: string,
  columns: GridColumn<Row>[],
): GridColumn<Row>[] {
  const { data } = useTenantReferenceQuery(["listing-layout", listingId], () => appSettingsApi.getListingLayout(listingId));

  return useMemo(
    () => applyListingLayout(columns, data?.result.columns),
    [columns, data?.result.columns],
  );
}
