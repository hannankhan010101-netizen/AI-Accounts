"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { PillTab, PillTabList } from "@/components/ui/pill-tab";
import type { CommandCenterPeriod, SalesGranularity } from "@/components/dashboard/command-center/types/command-center";
import { cn } from "@/lib/utils";

const PERIODS: { id: CommandCenterPeriod; label: string }[] = [
  { id: "mtd", label: "MTD" },
  { id: "qtd", label: "QTD" },
  { id: "ytd", label: "YTD" },
  { id: "fy", label: "FY" },
];

const GRANULARITY: { id: SalesGranularity; label: string }[] = [
  { id: "day", label: "Daily" },
  { id: "week", label: "Weekly" },
  { id: "month", label: "Monthly" },
];

export function StickyFilterBar({
  period,
  salesGranularity,
  onPeriodChange,
  onGranularityChange,
  editMode,
  onEditModeToggle,
  onRefresh,
  onSaveLayout,
  saving,
  periodLabel,
}: {
  period: CommandCenterPeriod;
  salesGranularity: SalesGranularity;
  onPeriodChange: (p: CommandCenterPeriod) => void;
  onGranularityChange: (g: SalesGranularity) => void;
  editMode: boolean;
  onEditModeToggle: () => void;
  onRefresh: () => void;
  onSaveLayout?: () => void;
  saving?: boolean;
  periodLabel?: string;
}) {
  return (
    <div
      className={cn(
        "surface-glass -mx-1 flex flex-wrap items-center justify-between gap-3 rounded-xl px-3 py-3",
        editMode && "ring-1 ring-brand-500/25",
      )}
    >
      <div className="flex flex-wrap items-center gap-4">
        <div className="flex flex-col gap-1.5">
          <span className="text-caption text-fg-muted">Period</span>
          <PillTabList aria-label="Period">
            {PERIODS.map((p) => (
              <PillTab key={p.id} active={period === p.id} onClick={() => onPeriodChange(p.id)}>
                {p.label}
              </PillTab>
            ))}
          </PillTabList>
        </div>
        <div className="hidden h-8 w-px bg-border-subtle sm:block" aria-hidden />
        <div className="flex flex-col gap-1.5">
          <span className="text-caption text-fg-muted">Sales trend</span>
          <PillTabList aria-label="Sales granularity">
            {GRANULARITY.map((g) => (
              <PillTab
                key={g.id}
                active={salesGranularity === g.id}
                onClick={() => onGranularityChange(g.id)}
              >
                {g.label}
              </PillTab>
            ))}
          </PillTabList>
        </div>
        {periodLabel ? (
          <span className="hidden self-end pb-1 text-xs text-fg-muted lg:inline">{periodLabel}</span>
        ) : null}
      </div>
      <div className="flex flex-wrap items-center gap-2">
        {editMode ? (
          <Badge variant="outline" className="border-brand-500/40 text-brand-700 dark:text-brand-300">
            Editing layout
          </Badge>
        ) : null}
        <Button type="button" size="sm" variant="outline" onClick={onRefresh}>
          Refresh
        </Button>
        <Button type="button" size="sm" variant={editMode ? "primary" : "outline"} onClick={onEditModeToggle}>
          {editMode ? "Done editing" : "Customize"}
        </Button>
        {editMode && onSaveLayout ? (
          <Button type="button" size="sm" onClick={onSaveLayout} disabled={saving}>
            {saving ? "Saving…" : "Save layout"}
          </Button>
        ) : null}
      </div>
    </div>
  );
}
