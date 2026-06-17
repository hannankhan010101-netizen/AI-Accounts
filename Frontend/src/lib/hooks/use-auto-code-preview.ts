"use client";

import { useEffect } from "react";

import { autoCodeApi } from "@/lib/api/tenant";
import { useTenantReferenceQuery } from "@/lib/api/tenant-query";

export type AutoCodeEntity =
  | "customer"
  | "supplier"
  | "product"
  | "nominal"
  | "location"
  | "project";

export function useAutoCodePreview(
  entity: AutoCodeEntity,
  {
    enabled = true,
    onPreview,
  }: { enabled?: boolean; onPreview?: (code: string | null, autoEnabled: boolean) => void } = {},
) {
  const query = useTenantReferenceQuery(["auto-code-peek", entity], () => autoCodeApi.peek(entity), { enabled });

  useEffect(() => {
    if (!query.data?.result) return;
    onPreview?.(query.data.result.nextCode ?? null, query.data.result.enabled);
  }, [query.data, onPreview]);

  return {
    enabled: query.data?.result.enabled ?? false,
    nextCode: query.data?.result.nextCode ?? null,
    isLoading: query.isLoading,
  };
}
