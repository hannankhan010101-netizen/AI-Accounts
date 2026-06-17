"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";

import { partiesApi } from "@/lib/api/tenant";

export function useCustomerNameMap() {
  const { data } = useTenantListQuery(["customers"], () => partiesApi.listCustomers());
  return useMemo(() => {
    const map = new Map<string, string>();
    for (const c of data?.result ?? []) {
      map.set(c.id, c.name || c.code || c.id);
    }
    return map;
  }, [data]);
}

export function useSupplierNameMap() {
  const { data } = useTenantListQuery(["suppliers"], () => partiesApi.listSuppliers());
  return useMemo(() => {
    const map = new Map<string, string>();
    for (const s of data?.result ?? []) {
      map.set(s.id, s.name || s.code || s.id);
    }
    return map;
  }, [data]);
}
