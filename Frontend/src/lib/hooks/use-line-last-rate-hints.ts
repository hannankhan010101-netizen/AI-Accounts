"use client";

import { useMemo } from "react";
import { useQueries } from "@tanstack/react-query";

import { lastRateApi } from "@/lib/api/tenant";
import { tenantQueryKey } from "@/lib/api/tenant-query";
import { useCompany } from "@/lib/auth/company-context";
import { setCurrentCompanyId } from "@/lib/auth/storage";
import type { LastRateDocType } from "@/lib/hooks/use-last-rate-settings";
import { useLastRateSettings } from "@/lib/hooks/use-last-rate-settings";
import { referenceQueryOptions } from "@/lib/query/options";

export interface LastRateLineContext {
  docType: LastRateDocType;
  partyKind: "customer" | "supplier";
  partyId: string;
}

function formatLastRateHint(row: {
  rate: string;
  documentNumber?: string | null;
  invoiceNumber?: string | null;
  billNumber?: string | null;
}): string {
  const docNo =
    row.documentNumber ?? row.invoiceNumber ?? row.billNumber ?? null;
  return docNo ? `Last: ${row.rate} (${docNo})` : `Last: ${row.rate}`;
}

/** Fetch last-rate hints for unique product codes when Smart Settings view mode is on. */
export function useLineLastRateHints(
  productCodes: string[],
  context: LastRateLineContext | undefined,
): Map<string, string> {
  const { companyId, isLoading: companyLoading } = useCompany();
  const { viewEnabled } = useLastRateSettings(context?.docType ?? "SI");
  const uniqueCodes = useMemo(
    () => [...new Set(productCodes.map((c) => c.trim()).filter(Boolean))],
    [productCodes],
  );

  const enabled =
    !companyLoading &&
    !!companyId &&
    viewEnabled &&
    !!context?.partyId &&
    uniqueCodes.length > 0;

  const queries = useQueries({
    queries: uniqueCodes.map((productCode) =>
      referenceQueryOptions({
        queryKey: tenantQueryKey(
          companyId,
          "last-rate-view",
          context?.partyKind,
          context?.partyId,
          context?.docType,
          productCode,
        ),
        queryFn: async () => {
          if (!context || !companyId) return null;
          setCurrentCompanyId(companyId);
          const res =
            context.partyKind === "customer"
              ? await lastRateApi.sales(
                  context.partyId,
                  productCode,
                  context.docType,
                  false,
                )
              : await lastRateApi.purchase(
                  context.partyId,
                  productCode,
                  context.docType,
                  false,
                );
          return res.result;
        },
        enabled,
      }),
    ),
  });

  return useMemo(() => {
    const map = new Map<string, string>();
    if (!enabled) return map;
    uniqueCodes.forEach((code, index) => {
      const row = queries[index]?.data;
      if (row?.rate) map.set(code, formatLastRateHint(row));
    });
    return map;
  }, [enabled, queries, uniqueCodes]);
}
