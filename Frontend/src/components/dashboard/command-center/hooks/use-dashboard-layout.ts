"use client";

import { useCallback, useMemo } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import type { DashboardLayoutSettings, GridLayoutItem } from "@/components/dashboard/command-center/types/command-center";
import { dashboardApi } from "@/lib/api/tenant";
import { useTenantReferenceQuery } from "@/lib/api/tenant-query";
import {
  DEFAULT_COMMAND_CENTER_LAYOUT,
  DEFAULT_DASHBOARD_VIEW,
  migrateDashboardWidgets,
} from "@/lib/dashboard/widget-catalog";
import { useCompany } from "@/lib/auth/company-context";

function normalizeLayout(raw: unknown): DashboardLayoutSettings {
  const body = raw && typeof raw === "object" ? (raw as Record<string, unknown>) : {};
  const widgets = migrateDashboardWidgets(body.widgets);
  const viewsRaw = body.views;
  const views =
    Array.isArray(viewsRaw) && viewsRaw.length > 0
      ? (viewsRaw as DashboardLayoutSettings["views"])
      : [DEFAULT_DASHBOARD_VIEW];
  const activeViewId =
    typeof body.activeViewId === "string" ? body.activeViewId : views[0]?.id ?? "default";
  const activeView = views.find((v) => v.id === activeViewId) ?? views[0] ?? DEFAULT_DASHBOARD_VIEW;
  return {
    widgets: [...widgets],
    views,
    activeViewId: activeView.id,
  };
}

export function useDashboardLayout() {
  const { companyId, isLoading: companyLoading } = useCompany();
  const qc = useQueryClient();

  const layoutQuery = useTenantReferenceQuery(
    ["dashboard-layout"],
    () => dashboardApi.getLayout(),
    { enabled: Boolean(companyId) && !companyLoading },
  );

  const settings = useMemo(
    () => normalizeLayout(layoutQuery.data?.result),
    [layoutQuery.data?.result],
  );

  const activeView = useMemo(
    () => settings.views.find((v) => v.id === settings.activeViewId) ?? DEFAULT_DASHBOARD_VIEW,
    [settings],
  );

  const visibleLayout = useMemo(() => {
    const widgetSet = new Set(settings.widgets);
    return activeView.layout.filter((item) => widgetSet.has(item.i));
  }, [activeView.layout, settings.widgets]);

  const saveMutation = useMutation({
    mutationFn: (next: DashboardLayoutSettings) => dashboardApi.putLayout(next),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["tenant", companyId, "dashboard-layout"] });
      void qc.invalidateQueries({ queryKey: ["tenant", companyId, "dashboard-settings"] });
    },
  });

  const saveLayout = useCallback(
    (layout: GridLayoutItem[]) => {
      const views = settings.views.map((v) =>
        v.id === activeView.id ? { ...v, layout } : v,
      );
      saveMutation.mutate({ ...settings, views });
    },
    [activeView.id, saveMutation, settings],
  );

  const resetLayout = useCallback(() => {
    saveMutation.mutate({
      ...settings,
      views: settings.views.map((v) =>
        v.id === activeView.id ? { ...v, layout: DEFAULT_COMMAND_CENTER_LAYOUT } : v,
      ),
    });
  }, [activeView.id, saveMutation, settings]);

  return {
    settings,
    activeView,
    visibleLayout,
    isLoading: layoutQuery.isLoading,
    saveLayout,
    resetLayout,
    saving: saveMutation.isPending,
  };
}
