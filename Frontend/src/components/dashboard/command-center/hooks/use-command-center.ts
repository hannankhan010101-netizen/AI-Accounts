"use client";

import { useCallback, useEffect, useState } from "react";

import type { CommandCenterPeriod, SalesGranularity } from "@/components/dashboard/command-center/types/command-center";
import { dashboardApi } from "@/lib/api/tenant";
import { useTenantReportQuery } from "@/lib/api/tenant-query";
import { useCompany } from "@/lib/auth/company-context";

const PERIOD_KEY = "fa.cc.period";
const GRAN_KEY = "fa.cc.granularity";

export function useCommandCenterFilters() {
  const [period, setPeriod] = useState<CommandCenterPeriod>("fy");
  const [salesGranularity, setSalesGranularity] = useState<SalesGranularity>("month");

  useEffect(() => {
    if (typeof window === "undefined") return;
    const p = sessionStorage.getItem(PERIOD_KEY) as CommandCenterPeriod | null;
    const g = sessionStorage.getItem(GRAN_KEY) as SalesGranularity | null;
    if (p) setPeriod(p);
    if (g) setSalesGranularity(g);
  }, []);

  const updatePeriod = useCallback((p: CommandCenterPeriod) => {
    setPeriod(p);
    sessionStorage.setItem(PERIOD_KEY, p);
  }, []);

  const updateGranularity = useCallback((g: SalesGranularity) => {
    setSalesGranularity(g);
    sessionStorage.setItem(GRAN_KEY, g);
  }, []);

  return { period, salesGranularity, setPeriod: updatePeriod, setSalesGranularity: updateGranularity };
}

export function useCommandCenter() {
  const { companyId, isLoading: companyLoading } = useCompany();
  const { period, salesGranularity, setPeriod, setSalesGranularity } = useCommandCenterFilters();

  const query = useTenantReportQuery(
    ["command-center", period, salesGranularity],
    () => dashboardApi.commandCenter({ period, salesGranularity }),
    { enabled: Boolean(companyId) && !companyLoading },
  );

  return {
    ...query,
    period,
    salesGranularity,
    setPeriod,
    setSalesGranularity,
    companyLoading,
    companyId,
  };
}
