"use client";

import Link from "next/link";
import { LayoutDashboard } from "lucide-react";

import { Sparkline } from "@/components/dashboard/command-center/sparkline";
import type { ExecutiveKpi, KpiStatus } from "@/components/dashboard/command-center/types/command-center";
import { AnimatedNumber } from "@/components/ui/animated-number";
import { Card } from "@/components/ui/card";
import { fmtAmount, fmtCompact } from "@/components/dashboard/dashboard-charts";
import { cn } from "@/lib/utils";

const STATUS_RING: Record<KpiStatus, string> = {
  good: "ring-status-success/25",
  warn: "ring-status-warning/30",
  critical: "ring-status-danger/35",
  neutral: "ring-border/40",
};

const STATUS_VALUE: Record<KpiStatus, string> = {
  good: "text-status-success",
  warn: "text-status-warning",
  critical: "text-status-danger",
  neutral: "text-fg",
};

export function ExecutiveKpiCard({ kpi }: { kpi: ExecutiveKpi }) {
  const invertNegative = kpi.id === "kpi-ar" || kpi.id === "kpi-ap";
  const trendUp = kpi.changePct !== null && (invertNegative ? kpi.changePct <= 0 : kpi.changePct >= 0);

  return (
    <Link href={kpi.drillDownHref} className="block min-w-[10rem] shrink-0 snap-start">
      <Card
        variant="glass"
        interactive
        className={cn(
          "card-bento h-full p-3.5 ring-1 motion-safe-transition hover:shadow-md",
          STATUS_RING[kpi.status],
        )}
      >
        <div className="flex items-start justify-between gap-2">
          <p className="text-caption font-medium normal-case tracking-normal text-fg-muted">{kpi.label}</p>
          <Sparkline values={kpi.trendSeries} positive={trendUp} label={kpi.label} />
        </div>
        <p className={cn("mt-2 text-section font-semibold tabular-nums tracking-tight", STATUS_VALUE[kpi.status])}>
          <AnimatedNumber
            value={parseFloat(kpi.value) || 0}
            format={(n) => fmtCompact(String(n))}
          />
        </p>
        <p className="mt-1 text-xs tabular-nums text-fg-muted" title={fmtAmount(kpi.value)}>
          {kpi.changePct !== null ? (
            <span className={cn(trendUp ? "text-status-success" : "text-status-danger")}>
              {kpi.changePct >= 0 ? "↑" : "↓"} {Math.abs(kpi.changePct).toFixed(1)}% vs prior
            </span>
          ) : (
            "No prior comparison"
          )}
        </p>
      </Card>
    </Link>
  );
}

export function ExecutiveKpiStrip({ kpis }: { kpis: ExecutiveKpi[] }) {
  return (
    <section
      className="-mx-1 flex snap-x snap-mandatory gap-3 overflow-x-auto pb-1 pt-0.5 scrollbar-thin"
      aria-label="Executive KPIs"
    >
      {kpis.map((kpi) => (
        <ExecutiveKpiCard key={kpi.id} kpi={kpi} />
      ))}
    </section>
  );
}
