"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { m } from "framer-motion";

import { CommandCenterSkeleton } from "@/components/dashboard/command-center/command-center-skeleton";
import { ExecutiveKpiStrip } from "@/components/dashboard/command-center/executive-kpi-strip";
import { useCommandCenter } from "@/components/dashboard/command-center/hooks/use-command-center";
import { useDashboardLayout } from "@/components/dashboard/command-center/hooks/use-dashboard-layout";
import { StickyFilterBar } from "@/components/dashboard/command-center/sticky-filter-bar";
import type { GridLayoutItem } from "@/components/dashboard/command-center/types/command-center";
import { WidgetGrid } from "@/components/dashboard/command-center/widget-grid";
import { TourMaturityBadge } from "@/components/tour/tour-maturity-badge";
import { TourWelcomeBanner } from "@/components/tour/tour-welcome-banner";
import { BrandMark } from "@/components/brand/brand-mark";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { InlineAlert } from "@/components/ui/inline-alert";
import { invalidateTenantQueries } from "@/lib/api/tenant-query";
import { useCompany } from "@/lib/auth/company-context";
import { filterWidgetsByModuleAccess, filterWidgetsByPermission } from "@/lib/dashboard/widget-catalog";
import { compactGridLayout } from "@/lib/dashboard/compact-grid-layout";
import { useMyPermissions } from "@/lib/rbac/use-my-permissions";
import { staggerContainer, staggerItem } from "@/lib/motion/variants";
import { useReducedMotion } from "@/lib/motion/use-reduced-motion";

export function CommandCenterDashboard() {
  const queryClient = useQueryClient();
  const reduced = useReducedMotion();
  const { companies, companyId } = useCompany();
  const companyName = companies.find((c) => c.id === companyId)?.name ?? "Your company";

  const {
    data,
    isLoading,
    isFetching,
    error,
    refetch,
    period,
    salesGranularity,
    setPeriod,
    setSalesGranularity,
    companyLoading,
  } = useCommandCenter();

  const { can, data: permsData } = useMyPermissions();

  const {
    settings,
    visibleLayout,
    saveLayout,
    resetLayout,
    isLoading: layoutLoading,
    saving,
  } = useDashboardLayout();

  const [editMode, setEditMode] = useState(false);
  const [draftLayout, setDraftLayout] = useState<GridLayoutItem[] | null>(null);

  const permittedWidgets = useMemo(() => {
    const modules = permsData?.result?.modules ?? [];
    const byPerm = filterWidgetsByPermission(settings.widgets, can);
    return filterWidgetsByModuleAccess(byPerm, modules);
  }, [can, permsData?.result?.modules, settings.widgets]);
  const widgetSet = useMemo(() => new Set(permittedWidgets), [permittedWidgets]);

  const layout = useMemo(() => {
    const base = draftLayout ?? visibleLayout;
    const filtered = base.filter((item) => widgetSet.has(item.i));
    return editMode ? filtered : compactGridLayout(filtered);
  }, [draftLayout, visibleLayout, widgetSet, editMode]);

  const payload = data?.result;
  const visibleKpis = useMemo(
    () => payload?.executiveKpis.filter((k) => widgetSet.has(k.id)) ?? [],
    [payload?.executiveKpis, widgetSet],
  );

  useEffect(() => {
    if (!editMode) setDraftLayout(null);
  }, [editMode, visibleLayout]);

  const handleRefresh = useCallback(() => {
    void refetch();
    void invalidateTenantQueries(queryClient, "command-center");
  }, [queryClient, refetch]);

  const handleSaveLayout = useCallback(() => {
    if (draftLayout) saveLayout(draftLayout);
    setEditMode(false);
  }, [draftLayout, saveLayout]);

  const handleResetLayout = useCallback(() => {
    resetLayout();
    setDraftLayout(null);
    setEditMode(false);
  }, [resetLayout]);

  const periodLabel = payload
    ? `${payload.period.from.slice(0, 10)} – ${payload.period.to.slice(0, 10)}`
    : undefined;

  if (companyLoading || isLoading || layoutLoading) {
    return <CommandCenterSkeleton />;
  }

  if (error instanceof Error) {
    return (
      <Card variant="glass" className="p-6">
        <InlineAlert variant="error" role="alert">
          Could not load dashboard: {error.message}
        </InlineAlert>
        <Button type="button" size="sm" className="mt-3" onClick={handleRefresh}>
          Retry
        </Button>
      </Card>
    );
  }

  if (!payload) {
    return (
      <EmptyState
        title="No dashboard data"
        description="We could not load your command center metrics. Try refreshing or check your connection."
        action={
          <Button type="button" size="sm" onClick={handleRefresh}>
            Refresh
          </Button>
        }
      />
    );
  }

  return (
    <m.div
      className="space-y-4"
      initial={reduced ? false : "hidden"}
      animate={reduced ? undefined : "visible"}
      variants={staggerContainer}
    >
      <m.header variants={staggerItem} className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <BrandMark className="h-7 w-7" />
            <h1 className="text-page-title font-semibold tracking-tight text-fg">Command Center</h1>
            <TourMaturityBadge />
            {editMode ? (
              <Badge variant="brand">Layout edit</Badge>
            ) : null}
          </div>
          <p className="mt-1 text-sm text-fg-muted">{companyName} · Business overview at a glance</p>
        </div>
        {isFetching ? <span className="text-xs text-fg-muted">Updating…</span> : null}
      </m.header>

      <TourWelcomeBanner />

      <StickyFilterBar
        period={period}
        salesGranularity={salesGranularity}
        onPeriodChange={setPeriod}
        onGranularityChange={setSalesGranularity}
        editMode={editMode}
        onEditModeToggle={() => setEditMode((v) => !v)}
        onRefresh={handleRefresh}
        onSaveLayout={draftLayout ? handleSaveLayout : undefined}
        saving={saving}
        periodLabel={periodLabel}
      />

      {editMode ? (
        <div className="flex flex-wrap gap-2">
          <Button type="button" size="sm" variant="outline" onClick={handleResetLayout} disabled={saving}>
            Reset to default
          </Button>
        </div>
      ) : null}

      {visibleKpis.length > 0 ? (
        <m.div variants={staggerItem}>
          <ExecutiveKpiStrip kpis={visibleKpis} />
        </m.div>
      ) : null}

      <m.div variants={staggerItem}>
        <WidgetGrid
          layout={layout}
          data={payload}
          editMode={editMode}
          onLayoutChange={setDraftLayout}
        />
      </m.div>
    </m.div>
  );
}
