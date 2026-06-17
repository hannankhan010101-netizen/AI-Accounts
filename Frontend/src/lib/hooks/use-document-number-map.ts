"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";

import { purchasesApi, salesApi } from "@/lib/api/tenant";

/** Map sales invoice id → document number for allocation grids and links. */
export function useInvoiceNumberMap() {
  const { data } = useTenantListQuery(["sales-invoices"], () => salesApi.listInvoices());
  return useMemo(() => {
    const map = new Map<string, string>();
    for (const inv of data?.result ?? []) {
      map.set(inv.id, String(inv.documentNumber ?? inv.id.slice(0, 8)));
    }
    return map;
  }, [data]);
}

/** Map supplier bill id → document number for allocation grids and links. */
export function useBillNumberMap() {
  const { data } = useTenantListQuery(["supplier-bills"], () => purchasesApi.listSupplierBills());
  return useMemo(() => {
    const map = new Map<string, string>();
    for (const bill of data?.result ?? []) {
      map.set(bill.id, String(bill.documentNumber ?? bill.id.slice(0, 8)));
    }
    return map;
  }, [data]);
}
