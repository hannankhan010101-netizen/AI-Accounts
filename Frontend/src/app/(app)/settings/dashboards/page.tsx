"use client";

import { invalidateTenantQueries, useTenantReferenceQuery } from "@/lib/api/tenant-query";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import type { DashboardLayoutSettings, DashboardView } from "@/components/dashboard/command-center/types/command-center";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { WorkspaceLoading } from "@/components/ui/workspace-loading";
import { dashboardApi } from "@/lib/api/tenant";
import {
  COMMAND_CENTER_WIDGET_CATALOG,
  DEFAULT_COMMAND_CENTER_LAYOUT,
  DEFAULT_COMMAND_CENTER_WIDGETS,
  DEFAULT_DASHBOARD_VIEW,
  migrateDashboardWidgets,
  ROLE_WIDGET_GROUPS,
} from "@/lib/dashboard/widget-catalog";

type RolePreset = keyof typeof ROLE_WIDGET_GROUPS;

function normalizeSettings(raw: unknown): DashboardLayoutSettings {
  const body = raw && typeof raw === "object" ? (raw as Record<string, unknown>) : {};
  const widgets = [...migrateDashboardWidgets(body.widgets)];
  const views =
    Array.isArray(body.views) && body.views.length > 0
      ? (body.views as DashboardView[])
      : [DEFAULT_DASHBOARD_VIEW];
  const activeViewId =
    typeof body.activeViewId === "string" ? body.activeViewId : views[0]?.id ?? "default";
  return { widgets, views, activeViewId };
}

export default function DashboardManagementPage() {
  const qc = useQueryClient();
  const [settings, setSettings] = useState<DashboardLayoutSettings>({
    widgets: [...DEFAULT_COMMAND_CENTER_WIDGETS],
    views: [DEFAULT_DASHBOARD_VIEW],
    activeViewId: "default",
  });
  const [newViewName, setNewViewName] = useState("");

  const { data, isLoading, error } = useTenantReferenceQuery(["dashboard-layout"], () =>
    dashboardApi.getLayout(),
  );

  useEffect(() => {
    if (data?.result) setSettings(normalizeSettings(data.result));
  }, [data?.result]);

  const activeView = useMemo(
    () => settings.views.find((v) => v.id === settings.activeViewId) ?? settings.views[0],
    [settings],
  );

  const groups = useMemo(() => {
    const map = new Map<number, typeof COMMAND_CENTER_WIDGET_CATALOG>();
    for (const w of COMMAND_CENTER_WIDGET_CATALOG) {
      if (w.kpiOnly) continue;
      const list = map.get(w.row) ?? [];
      list.push(w);
      map.set(w.row, list);
    }
    return [...map.entries()].sort(([a], [b]) => a - b);
  }, []);

  const kpiWidgets = useMemo(
    () => COMMAND_CENTER_WIDGET_CATALOG.filter((w) => w.kpiOnly),
    [],
  );

  const save = useMutation({
    mutationFn: () => dashboardApi.putLayout(settings),
    onSuccess: () => {
      void invalidateTenantQueries(qc, "dashboard-layout");
      void invalidateTenantQueries(qc, "dashboard-settings");
    },
  });

  const toggleWidget = useCallback((id: string, on: boolean) => {
    setSettings((prev) => ({
      ...prev,
      widgets: on ? [...new Set([...prev.widgets, id])] : prev.widgets.filter((w) => w !== id),
    }));
  }, []);

  const selectAll = useCallback((on: boolean) => {
    setSettings((prev) => ({
      ...prev,
      widgets: on ? [...DEFAULT_COMMAND_CENTER_WIDGETS] : [],
    }));
  }, []);

  const applyRolePreset = useCallback((preset: RolePreset) => {
    const widgets = [...(ROLE_WIDGET_GROUPS[preset] ?? ROLE_WIDGET_GROUPS.owner)];
    setSettings((prev) => ({
      ...prev,
      widgets,
      views: prev.views.map((v) =>
        v.id === prev.activeViewId
          ? { ...v, rolePreset: preset as DashboardView["rolePreset"], layout: DEFAULT_COMMAND_CENTER_LAYOUT }
          : v,
      ),
    }));
  }, []);

  const setActiveView = useCallback((viewId: string) => {
    setSettings((prev) => ({ ...prev, activeViewId: viewId }));
  }, []);

  const renameView = useCallback((viewId: string, name: string) => {
    setSettings((prev) => ({
      ...prev,
      views: prev.views.map((v) => (v.id === viewId ? { ...v, name } : v)),
    }));
  }, []);

  const duplicateView = useCallback(() => {
    const id = `view-${Date.now()}`;
    const source = activeView ?? DEFAULT_DASHBOARD_VIEW;
    setSettings((prev) => ({
      ...prev,
      views: [...prev.views, { ...source, id, name: `${source.name} copy`, isDefault: false }],
      activeViewId: id,
    }));
  }, [activeView]);

  const deleteView = useCallback((viewId: string) => {
    setSettings((prev) => {
      if (prev.views.length <= 1) return prev;
      const views = prev.views.filter((v) => v.id !== viewId);
      const activeViewId = prev.activeViewId === viewId ? views[0]?.id ?? "default" : prev.activeViewId;
      return { ...prev, views, activeViewId };
    });
  }, []);

  const addView = useCallback(() => {
    const name = newViewName.trim() || "Custom view";
    const id = `view-${Date.now()}`;
    setSettings((prev) => ({
      ...prev,
      views: [
        ...prev.views,
        {
          id,
          name,
          layout: DEFAULT_COMMAND_CENTER_LAYOUT,
          isDefault: false,
          rolePreset: "owner",
        },
      ],
      activeViewId: id,
    }));
    setNewViewName("");
  }, [newViewName]);

  const rowLabels: Record<number, string> = {
    1: "Executive KPIs",
    2: "Cashflow & Sales",
    3: "Business Health",
    4: "Inventory",
    5: "Profitability",
    6: "Activity",
    7: "Insights",
  };

  return (
    <div>
      <PageHeader
        title="Dashboard management"
        breadcrumb="Settings / Dashboard management"
        description="Configure widgets, saved views, and role presets for the command center."
      />
      {isLoading ? <WorkspaceLoading className="mt-4" /> : null}
      {error instanceof Error ? (
        <p className="mt-4 text-sm text-status-danger">{error.message}</p>
      ) : null}

      <div className="mt-4 grid gap-6 lg:grid-cols-2">
        <section className="space-y-5 rounded-lg border border-border bg-surface p-6">
          <h2 className="text-sm font-semibold text-fg">Saved views</h2>
          <ul className="space-y-2">
            {settings.views.map((view) => (
              <li
                key={view.id}
                className="flex flex-wrap items-center gap-2 rounded-md border border-border/60 px-3 py-2"
              >
                <Button
                  type="button"
                  size="sm"
                  variant={settings.activeViewId === view.id ? "primary" : "outline"}
                  onClick={() => setActiveView(view.id)}
                >
                  {settings.activeViewId === view.id ? "Active" : "Use"}
                </Button>
                <Input
                  value={view.name}
                  onChange={(e) => renameView(view.id, e.target.value)}
                  className="h-8 max-w-[12rem] text-sm"
                  aria-label={`Rename ${view.name}`}
                />
                {view.isDefault ? (
                  <span className="text-xs text-fg-muted">Default</span>
                ) : (
                  <Button type="button" size="sm" variant="ghost" onClick={() => deleteView(view.id)}>
                    Delete
                  </Button>
                )}
              </li>
            ))}
          </ul>
          <div className="flex flex-wrap gap-2">
            <Input
              placeholder="New view name"
              value={newViewName}
              onChange={(e) => setNewViewName(e.target.value)}
              className="h-9 max-w-[14rem]"
            />
            <Button type="button" size="sm" variant="outline" onClick={addView}>
              Add view
            </Button>
            <Button type="button" size="sm" variant="outline" onClick={duplicateView}>
              Duplicate active
            </Button>
          </div>
        </section>

        <section className="space-y-4 rounded-lg border border-border bg-surface p-6">
          <h2 className="text-sm font-semibold text-fg">Role preset</h2>
          <p className="text-xs text-fg-muted">
            Applies a starter widget set for the active view. You can override individual widgets below.
          </p>
          <div className="flex flex-wrap gap-2">
            {(Object.keys(ROLE_WIDGET_GROUPS) as RolePreset[]).map((preset) => (
              <Button key={preset} type="button" size="sm" variant="outline" onClick={() => applyRolePreset(preset)}>
                {preset.charAt(0).toUpperCase() + preset.slice(1)}
              </Button>
            ))}
          </div>
        </section>
      </div>

      <section className="mt-6 max-w-2xl space-y-5 rounded-lg border border-border bg-surface p-6">
        <div className="flex flex-wrap gap-2">
          <Button type="button" variant="outline" size="sm" onClick={() => selectAll(true)}>
            Select all
          </Button>
          <Button type="button" variant="outline" size="sm" onClick={() => selectAll(false)}>
            Clear all
          </Button>
        </div>

        <div>
          <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-fg-muted">
            Row 1 · {rowLabels[1]}
          </h2>
          <div className="space-y-2">
            {kpiWidgets.map((w) => (
              <label key={w.id} className="flex items-center gap-2 text-sm">
                <Checkbox
                  checked={settings.widgets.includes(w.id)}
                  onChange={(e) => toggleWidget(w.id, e.target.checked)}
                />
                {w.label}
              </label>
            ))}
          </div>
        </div>

        {groups.map(([row, widgets]) => (
          <div key={row}>
            <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-fg-muted">
              Row {row} · {rowLabels[row] ?? "Widgets"}
            </h2>
            <div className="space-y-2">
              {widgets.map((w) => (
                <label key={w.id} className="flex items-center gap-2 text-sm">
                  <Checkbox
                    checked={settings.widgets.includes(w.id)}
                    onChange={(e) => toggleWidget(w.id, e.target.checked)}
                  />
                  {w.label}
                </label>
              ))}
            </div>
          </div>
        ))}

        <Button type="button" disabled={save.isPending} onClick={() => save.mutate()}>
          {save.isPending ? "Saving…" : "Save dashboard settings"}
        </Button>
      </section>
    </div>
  );
}
