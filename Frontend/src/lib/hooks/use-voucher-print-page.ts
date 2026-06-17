"use client";

import type { UseQueryResult } from "@tanstack/react-query";

import { useTenantDetailQuery } from "@/lib/api/tenant-query";
import { useBusinessPrintHeader } from "@/lib/hooks/use-business-print";
import { usePrintTemplate } from "@/lib/hooks/use-print-template";
import type { PrintTemplateSettings } from "@/lib/api/tenant";

/** Shared loading state for voucher print routes (document + business header + template). */
export function useVoucherPrintPage<TData>(
  queryKey: unknown[],
  queryFn: () => Promise<TData>,
  enabled: boolean,
  templateCode?: string,
): {
  query: UseQueryResult<TData>;
  businessName: string | null;
  businessAddress: string | null;
  businessLogoUrl: string | null;
  template: PrintTemplateSettings | undefined;
  isLoading: boolean;
  error: unknown;
} {
  const biz = useBusinessPrintHeader();
  const templateQuery = usePrintTemplate(templateCode ?? "");
  const query = useTenantDetailQuery(queryKey, queryFn, { enabled, retry: false });

  const templateLoading = Boolean(templateCode) && templateQuery.isLoading;

  return {
    query,
    businessName: biz.businessName,
    businessAddress: biz.businessAddress,
    businessLogoUrl: biz.businessLogoUrl,
    template: templateCode ? templateQuery.data?.result : undefined,
    isLoading: query.isLoading || biz.isLoading || templateLoading,
    error: query.error ?? templateQuery.error,
  };
}
