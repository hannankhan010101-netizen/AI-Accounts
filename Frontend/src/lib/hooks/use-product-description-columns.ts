"use client";
import { useTenantReferenceQuery } from "@/lib/api/tenant-query";

import { useMemo } from "react";


import { settingsApi } from "@/lib/api/tenant";


import {
  parseProductDescriptionColumns,
  type ProductDescriptionColumn,
  type ProductDescriptionDocType,
} from "./product-description-columns";

export function useProductDescriptionColumns(docType: ProductDescriptionDocType) {
  const { data, isLoading } = useTenantReferenceQuery(["smart-settings"], () => settingsApi.getSmartSettings());

  const columns = useMemo((): ProductDescriptionColumn[] => {
    const payload = data?.result?.payload as Record<string, unknown> | undefined;
    return parseProductDescriptionColumns(payload?.productDescription, docType);
  }, [data, docType]);

  return { columns, isLoading };
}

export type { ProductDescriptionColumn, ProductDescriptionDocType };
