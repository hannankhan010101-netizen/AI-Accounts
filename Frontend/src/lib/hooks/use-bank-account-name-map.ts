"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";

import { bankApi } from "@/lib/api/tenant";

export function useBankAccountNameMap() {
  const { data } = useTenantListQuery(["bank-accounts"], () => bankApi.listAccounts());

  return useMemo(() => {
    const map = new Map<string, string>();
    for (const a of data?.result ?? []) {
      const label = a.name ? `${a.code ? `${a.code} — ` : ""}${a.name}` : a.code ?? a.id;
      map.set(a.id, label);
    }
    return map;
  }, [data]);
}
