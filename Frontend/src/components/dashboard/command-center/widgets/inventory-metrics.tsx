"use client";

import { Package, TrendingUp } from "lucide-react";

import { AnimatedNumber } from "@/components/ui/animated-number";
import type { CommandCenterPayload } from "@/components/dashboard/command-center/types/command-center";
import { fmtAmount, fmtCompact } from "@/components/dashboard/dashboard-charts";
import { cn } from "@/lib/utils";

function parseNum(raw: string): number {
  const n = parseFloat(raw);
  return Number.isFinite(n) ? n : 0;
}

function StockBadge({ label, count, tone }: { label: string; count: number; tone?: "default" | "warn" | "danger" }) {
  const toneClass =
    tone === "danger"
      ? "bg-status-danger/10 text-status-danger"
      : tone === "warn"
        ? "bg-status-warning/10 text-status-warning"
        : "bg-surface-muted/80 text-fg-muted";

  return (
    <span className={cn("inline-flex items-center rounded-md px-2 py-0.5 text-[10px] font-medium tabular-nums", toneClass)}>
      {count} {label}
    </span>
  );
}

export function InventoryValueMetric({ data }: { data: CommandCenterPayload["inventoryCommand"] }) {
  const value = parseNum(data.totalValue);
  const buckets = data.bucketCounts;

  return (
    <div className="flex h-full flex-col justify-between gap-3">
      <div>
        <p className="text-3xl font-semibold tabular-nums tracking-tight text-fg">
          <AnimatedNumber value={value} format={(n) => fmtCompact(String(n))} />
        </p>
        <p className="mt-1 text-xs text-fg-muted" title={fmtAmount(data.totalValue)}>
          At cost · {fmtAmount(data.totalValue)}
        </p>
      </div>
      <div className="flex flex-wrap gap-1.5">
        <StockBadge label="in stock" count={buckets.inStock} />
        {buckets.lowStock > 0 ? <StockBadge label="low" count={buckets.lowStock} tone="warn" /> : null}
        {buckets.outOfStock > 0 ? <StockBadge label="OOS" count={buckets.outOfStock} tone="danger" /> : null}
      </div>
    </div>
  );
}

export function InventoryTurnoverMetric({ ratio }: { ratio: number | null }) {
  if (ratio === null) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 py-2 text-center">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-surface-muted/60 text-fg-muted">
          <Package className="h-5 w-5" aria-hidden />
        </div>
        <div>
          <p className="text-sm font-medium text-fg">Not available</p>
          <p className="mt-0.5 max-w-[12rem] text-[11px] leading-snug text-fg-muted">
            Requires inventory value and COGS in the selected period.
          </p>
        </div>
      </div>
    );
  }

  const pct = Math.min(ratio * 25, 100);
  const healthy = ratio >= 4;
  const low = ratio < 2;
  const stroke = low ? "var(--status-warning)" : healthy ? "var(--status-success)" : "var(--brand-600)";

  return (
    <div className="flex h-full items-center gap-4">
      <div className="relative h-16 w-16 shrink-0">
        <svg viewBox="0 0 36 36" className="h-full w-full -rotate-90" aria-hidden>
          <circle cx="18" cy="18" r="15.5" fill="none" stroke="var(--border)" strokeWidth="2.5" />
          <circle
            cx="18"
            cy="18"
            r="15.5"
            fill="none"
            stroke={stroke}
            strokeWidth="2.5"
            strokeDasharray={`${pct} 100`}
            strokeLinecap="round"
          />
        </svg>
        <span className="absolute inset-0 flex items-center justify-center text-base font-bold tabular-nums text-fg">
          {ratio.toFixed(1)}
        </span>
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-1.5 text-xs font-medium text-fg">
          <TrendingUp className="h-3.5 w-3.5 text-brand-600" aria-hidden />
          Turnover ratio
        </div>
        <p className="mt-1 text-[11px] leading-snug text-fg-muted">
          {healthy
            ? "Healthy stock rotation for the period."
            : low
              ? "Slow-moving inventory — review reorder levels."
              : "Moderate turnover — monitor fast movers."}
        </p>
      </div>
    </div>
  );
}
