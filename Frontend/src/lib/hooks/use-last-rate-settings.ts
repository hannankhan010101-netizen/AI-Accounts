"use client";
import { useTenantReferenceQuery } from "@/lib/api/tenant-query";

import { useMemo } from "react";


import { settingsApi } from "@/lib/api/tenant";


export type LastRateDocType = "PO" | "QO" | "SC" | "SI" | "SO" | "VC" | "VI";

type LastRateBlock = { addEdit?: boolean; view?: boolean };

/** Whether Last Rate is enabled for a document type (Smart Settings §12.2.7). */
export function useLastRateSettings(docType: LastRateDocType) {
  const { data, isLoading } = useTenantReferenceQuery(["smart-settings"], () => settingsApi.getSmartSettings());

  const block = useMemo((): LastRateBlock => {
    const payload = data?.result?.payload as Record<string, unknown> | undefined;
    const lastRate = payload?.lastRate;
    if (!lastRate || typeof lastRate !== "object") return {};
    const row = (lastRate as Record<string, unknown>)[docType];
    if (!row || typeof row !== "object") return {};
    return row as LastRateBlock;
  }, [data, docType]);

  return {
    addEditEnabled: Boolean(block.addEdit),
    viewEnabled: Boolean(block.view),
    isLoading,
  };
}
