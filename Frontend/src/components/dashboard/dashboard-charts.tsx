"use client";

import Decimal from "decimal.js";
import { m } from "framer-motion";
import { useEffect, useMemo, useState } from "react";

import {
  calcMoMChange,
  fmtAmount,
  fmtCompact,
  fmtMonthLong,
  fmtMonthShort,
  parseAmount,
  pctOf,
} from "@/components/dashboard/chart-utils";
import { appPresets } from "@/lib/motion/app-presets";
import { useReducedMotion } from "@/lib/motion/use-reduced-motion";
import { cn } from "@/lib/utils";

export { fmtAmount, fmtCompact } from "@/components/dashboard/chart-utils";

const CHART_HEIGHT_PX = 128;

function useChartMount(): boolean {
  const reduced = useReducedMotion();
  const [mounted, setMounted] = useState(reduced);
  useEffect(() => {
    if (reduced) return;
    const t = requestAnimationFrame(() => setMounted(true));
    return () => cancelAnimationFrame(t);
  }, [reduced]);
  return mounted || reduced;
}

function ChartSummaryBar({
  items,
}: {
  items: { label: string; value: string; hint?: string; tone?: string }[];
}) {
  return (
    <div className="mb-4 grid grid-cols-2 gap-3 sm:grid-cols-3">
      {items.map((item) => (
        <div key={item.label} className="min-w-0 rounded-lg bg-surface-muted/40 px-2.5 py-2 dark:bg-surface-muted/20">
          <p className="text-[10px] font-medium uppercase tracking-wide text-fg-muted">{item.label}</p>
          <p className={cn("mt-0.5 truncate text-sm font-semibold tabular-nums", item.tone ?? "text-fg")}>
            {item.value}
          </p>
          {item.hint ? <p className="mt-0.5 truncate text-[10px] text-fg-muted">{item.hint}</p> : null}
        </div>
      ))}
    </div>
  );
}

function TrendBadge({ pct, label = "vs prior" }: { pct: number | null; label?: string }) {
  if (pct === null || !Number.isFinite(pct)) return null;
  const positive = pct >= 0;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-0.5 rounded-md px-1.5 py-0.5 text-[10px] font-semibold tabular-nums",
        positive
          ? "bg-status-success/12 text-status-success"
          : "bg-status-danger/12 text-status-danger",
      )}
      title={label}
    >
      {positive ? "↑" : "↓"} {Math.abs(pct).toFixed(1)}%
    </span>
  );
}

function ChartTooltip({
  title,
  lines,
  visible,
}: {
  title: string;
  lines: string[];
  visible: boolean;
}) {
  if (!visible) return null;
  return (
    <div
      role="tooltip"
      className="pointer-events-none absolute bottom-full left-1/2 z-20 mb-2 w-max max-w-[12rem] -translate-x-1/2 rounded-lg border border-border/60 bg-surface-elevated px-2.5 py-2 text-[10px] shadow-lg dark:shadow-premium"
    >
      <p className="font-semibold text-fg">{title}</p>
      {lines.map((line) => (
        <p key={line} className="mt-0.5 tabular-nums text-fg-muted">
          {line}
        </p>
      ))}
    </div>
  );
}

function ChartEmpty({ message, hint }: { message: string; hint?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-10 text-center">
      <p className="text-sm text-fg-muted">{message}</p>
      {hint ? <p className="mt-1 max-w-xs text-xs text-fg-muted/80">{hint}</p> : null}
    </div>
  );
}

export function BarChart({
  data,
  valueKey,
  labelKey,
  className,
  barClassName = "bg-chart-1 dark:bg-chart-2",
}: {
  data: { [key: string]: string }[];
  valueKey: string;
  labelKey: string;
  className?: string;
  barClassName?: string;
}) {
  const reduced = useReducedMotion();
  const mounted = useChartMount();
  const [hovered, setHovered] = useState<number | null>(null);

  const parsed = useMemo(
    () =>
      data.map((d) => ({
        label: String(d[labelKey]),
        value: parseAmount(String(d[valueKey] ?? 0)).toNumber(),
        raw: String(d[valueKey] ?? 0),
      })),
    [data, valueKey, labelKey],
  );

  if (!parsed.length) {
    return (
      <ChartEmpty
        message="No sales recorded this period."
        hint="Post sales invoices to see monthly revenue trends."
      />
    );
  }

  const values = parsed.map((p) => p.value);
  const total = values.reduce((a, b) => a + b, 0);
  const avg = total / values.length;
  const max = Math.max(...values, 1);
  const peakIdx = values.indexOf(Math.max(...values));
  const latestIdx = values.length - 1;
  const latestMoM = calcMoMChange(values[latestIdx] ?? 0, values[latestIdx - 1] ?? null);
  const peak = parsed[peakIdx];

  return (
    <div className={className}>
      <ChartSummaryBar
        items={[
          { label: "FY total", value: fmtCompact(total), hint: fmtAmount(String(total)) },
          {
            label: "Monthly avg",
            value: fmtCompact(avg),
            hint: `${parsed.length} months`,
          },
          {
            label: "Latest month",
            value: fmtCompact(values[latestIdx] ?? 0),
            hint: latestMoM !== null ? undefined : "First period",
            tone:
              latestMoM === null
                ? undefined
                : latestMoM >= 0
                  ? "text-status-success"
                  : "text-status-danger",
          },
        ]}
      />
      {peak ? (
        <p className="mb-3 text-[11px] text-fg-muted">
          Peak: <span className="font-medium text-fg">{fmtMonthLong(peak.label)}</span> at{" "}
          {fmtCompact(peak.value)}
          {latestMoM !== null ? (
            <>
              {" "}
              · Latest <TrendBadge pct={latestMoM} label="Month-over-month change" />
            </>
          ) : null}
        </p>
      ) : null}
      <div className="relative">
        <div
          className="pointer-events-none absolute inset-x-0 border-t border-dashed border-border/50"
          style={{ bottom: 24 + (avg / max) * CHART_HEIGHT_PX }}
          aria-hidden
        />
        <div className="relative flex h-40 items-end gap-1">
          {parsed.map((p, i) => {
            const barHeightPx = Math.max(4, Math.round((p.value / max) * CHART_HEIGHT_PX));
            const mom = calcMoMChange(p.value, i > 0 ? values[i - 1]! : null);
            const share = pctOf(p.value, total);
            const isPeak = i === peakIdx;
            return (
              <div
                key={`${p.label}-${i}`}
                className="relative flex min-w-0 flex-1 flex-col items-center justify-end gap-1"
                style={{ height: CHART_HEIGHT_PX }}
                onMouseEnter={() => setHovered(i)}
                onMouseLeave={() => setHovered(null)}
              >
                <ChartTooltip
                  title={fmtMonthLong(p.label)}
                  lines={[
                    fmtAmount(p.raw),
                    `${share.toFixed(1)}% of FY sales`,
                    mom !== null ? `${mom >= 0 ? "+" : ""}${mom.toFixed(1)}% vs prior month` : "First month",
                  ]}
                  visible={hovered === i}
                />
                <m.div
                  className={cn(
                    "w-full max-w-[2rem] rounded-t origin-bottom transition-shadow",
                    barClassName,
                    isPeak && "ring-2 ring-brand-500/40 ring-offset-1 ring-offset-surface",
                    hovered === i && "opacity-100",
                    hovered !== null && hovered !== i && "opacity-50",
                  )}
                  initial={reduced ? false : { scaleY: 0 }}
                  animate={{ scaleY: mounted ? 1 : 0 }}
                  transition={{
                    ...appPresets.barGrow.transition,
                    delay: reduced ? 0 : i * 0.04,
                  }}
                  style={{ height: barHeightPx }}
                  tabIndex={0}
                  role="img"
                  aria-label={`${fmtMonthLong(p.label)}: ${fmtAmount(p.raw)}`}
                  onFocus={() => setHovered(i)}
                  onBlur={() => setHovered(null)}
                />
                <span className="max-w-full truncate text-[9px] font-medium text-fg-muted">
                  {fmtMonthShort(p.label)}
                </span>
              </div>
            );
          })}
        </div>
        <p className="mt-1 text-[9px] text-fg-muted/70">Dashed line = monthly average</p>
      </div>
    </div>
  );
}

export function DualBarChart({
  data,
  inKey,
  outKey,
  labelKey,
}: {
  data: { month: string; inflow: string; outflow: string; net?: string }[];
  inKey: string;
  outKey: string;
  labelKey: string;
}) {
  const reduced = useReducedMotion();
  const mounted = useChartMount();
  const [hovered, setHovered] = useState<number | null>(null);

  const pairs = useMemo(
    () =>
      data.map((d) => {
        const inflow = parseAmount(String(d[inKey as keyof typeof d] ?? 0)).toNumber();
        const outflow = parseAmount(String(d[outKey as keyof typeof d] ?? 0)).toNumber();
        return {
          label: String(d[labelKey as keyof typeof d]),
          inflow,
          outflow,
          net: inflow - outflow,
        };
      }),
    [data, inKey, outKey, labelKey],
  );

  if (!pairs.length) {
    return (
      <ChartEmpty
        message="No cash movement in this range."
        hint="Bank receipts and payments will appear here."
      />
    );
  }

  const totalIn = pairs.reduce((s, p) => s + p.inflow, 0);
  const totalOut = pairs.reduce((s, p) => s + p.outflow, 0);
  const netTotal = totalIn - totalOut;
  const max = Math.max(...pairs.flatMap((p) => [p.inflow, p.outflow]), 1);

  return (
    <div>
      <ChartSummaryBar
        items={[
          { label: "Total in", value: fmtCompact(totalIn), tone: "text-status-success" },
          { label: "Total out", value: fmtCompact(totalOut), tone: "text-status-warning" },
          {
            label: "Net cash",
            value: fmtCompact(netTotal),
            tone: netTotal >= 0 ? "text-status-success" : "text-status-danger",
            hint: netTotal >= 0 ? "Positive flow" : "Net outflow",
          },
        ]}
      />
      <div className="mb-2 flex gap-4 text-[10px] text-fg-muted">
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-sm bg-status-success" /> Inflow
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-sm bg-status-warning" /> Outflow
        </span>
      </div>
      <div className="min-w-0">
        <div className="flex items-end gap-1" style={{ height: CHART_HEIGHT_PX }}>
          {pairs.map((p, i) => {
            const inH = Math.max(4, Math.round((p.inflow / max) * CHART_HEIGHT_PX));
            const outH = Math.max(4, Math.round((p.outflow / max) * CHART_HEIGHT_PX));
            return (
              <div
                key={p.label}
                className="relative flex min-w-[1.75rem] flex-1 flex-col items-center justify-end"
                onMouseEnter={() => setHovered(i)}
                onMouseLeave={() => setHovered(null)}
              >
                <ChartTooltip
                  title={fmtMonthLong(p.label)}
                  lines={[
                    `In: ${fmtCompact(p.inflow)}`,
                    `Out: ${fmtCompact(p.outflow)}`,
                    `Net: ${fmtCompact(p.net)}`,
                  ]}
                  visible={hovered === i}
                />
                <div className="flex w-full max-w-[2.5rem] items-end justify-center gap-px">
                  <m.div
                    className="w-1/2 origin-bottom rounded-t bg-status-success"
                    initial={reduced ? false : { scaleY: 0 }}
                    animate={{ scaleY: mounted ? 1 : 0 }}
                    transition={{ ...appPresets.barGrow.transition, delay: reduced ? 0 : i * 0.04 }}
                    style={{ height: inH }}
                    aria-hidden
                  />
                  <m.div
                    className="w-1/2 origin-bottom rounded-t bg-status-warning"
                    initial={reduced ? false : { scaleY: 0 }}
                    animate={{ scaleY: mounted ? 1 : 0 }}
                    transition={{
                      ...appPresets.barGrow.transition,
                      delay: reduced ? 0 : i * 0.04 + 0.02,
                    }}
                    style={{ height: outH }}
                    aria-hidden
                  />
                </div>
              </div>
            );
          })}
        </div>
        <div className="mt-1.5 flex gap-1 border-t border-border/40 pt-1.5">
          {pairs.map((p) => (
            <div
              key={`${p.label}-axis`}
              className="flex min-w-[1.75rem] flex-1 flex-col items-center gap-0.5 text-center"
            >
              <span className="w-full truncate text-[9px] font-medium text-fg-muted">
                {fmtMonthShort(p.label)}
              </span>
              <span
                className={cn(
                  "w-full truncate text-[8px] font-semibold tabular-nums leading-none",
                  p.net >= 0 ? "text-status-success" : "text-status-danger",
                )}
                title={`Net ${fmtCompact(p.net)}`}
              >
                {p.net >= 0 ? "+" : ""}
                {fmtCompact(p.net)}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function DonutChart({
  segments,
}: {
  segments: { label: string; amount: string; color: string }[];
}) {
  const reduced = useReducedMotion();
  const mounted = useChartMount();
  const [hovered, setHovered] = useState<string | null>(null);

  const parsed = useMemo(
    () =>
      segments
        .map((s) => ({
          ...s,
          value: parseAmount(s.amount).toNumber(),
        }))
        .filter((s) => s.value > 0)
        .sort((a, b) => b.value - a.value),
    [segments],
  );

  const total = parsed.reduce((a, s) => a + s.value, 0);
  if (total <= 0) {
    return (
      <ChartEmpty
        message="No expense breakdown yet."
        hint="Expenses will group by category once bills are posted."
      />
    );
  }

  const top = parsed[0];
  const topShare = top ? pctOf(top.value, total) : 0;

  let cumulative = 0;
  const stops = parsed
    .map((s) => {
      const start = (cumulative / total) * 100;
      cumulative += s.value;
      const end = (cumulative / total) * 100;
      return `${s.color} ${start}% ${end}%`;
    })
    .join(", ");

  return (
    <div>
      {top ? (
        <p className="mb-3 text-[11px] leading-relaxed text-fg-muted">
          <span className="font-medium text-fg">{top.label}</span> is {topShare.toFixed(0)}% of FY
          expenses ({fmtCompact(top.value)}).
        </p>
      ) : null}
      <div className="flex flex-col items-center gap-4 sm:flex-row sm:items-start">
        <div className="relative shrink-0">
          <m.div
            className="h-32 w-32 rounded-full"
            style={{ background: `conic-gradient(${stops})` }}
            role="img"
            aria-label="Expense breakdown chart"
            initial={reduced ? false : { scale: 0.85, opacity: 0 }}
            animate={{ scale: mounted ? 1 : 0.85, opacity: mounted ? 1 : 0 }}
            transition={appPresets.barGrow.transition}
          />
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <div className="flex h-[4.5rem] w-[4.5rem] flex-col items-center justify-center rounded-full bg-surface shadow-inner">
              <span className="text-[9px] uppercase tracking-wide text-fg-muted">Total</span>
              <span className="text-sm font-bold tabular-nums text-fg">{fmtCompact(total)}</span>
            </div>
          </div>
        </div>
        <ul className="min-w-0 flex-1 space-y-1.5 text-xs">
          {parsed.map((s) => {
            const share = pctOf(s.value, total);
            return (
              <li
                key={s.label}
                className={cn(
                  "flex cursor-default items-center justify-between gap-2 rounded-md px-2 py-1.5 motion-safe-transition",
                  hovered === s.label && "bg-surface-muted/60",
                  hovered && hovered !== s.label && "opacity-60",
                )}
                onMouseEnter={() => setHovered(s.label)}
                onMouseLeave={() => setHovered(null)}
              >
                <span className="flex min-w-0 items-center gap-1.5">
                  <span className="h-2.5 w-2.5 shrink-0 rounded-sm" style={{ background: s.color }} />
                  <span className="truncate text-fg">{s.label}</span>
                </span>
                <span className="shrink-0 text-right">
                  <span className="block font-semibold tabular-nums text-fg">{share.toFixed(1)}%</span>
                  <span className="block text-[10px] tabular-nums text-fg-muted">{fmtCompact(s.value)}</span>
                </span>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}

export function LineAreaChart({
  data,
}: {
  data: { month: string; balance: string }[];
}) {
  const reduced = useReducedMotion();
  const mounted = useChartMount();
  const [hovered, setHovered] = useState<number | null>(null);

  const points = useMemo(
    () =>
      data.map((d, i) => ({
        x: i,
        y: parseAmount(d.balance).toNumber(),
        label: d.month,
        raw: d.balance,
      })),
    [data],
  );

  if (!points.length) {
    return (
      <ChartEmpty
        message="No bank balance history."
        hint="Balances update as bank transactions are posted."
      />
    );
  }

  const minY = Math.min(...points.map((p) => p.y));
  const maxY = Math.max(...points.map((p) => p.y), minY + 1);
  const latest = points[points.length - 1]!;
  const first = points[0]!;
  const change = latest.y - first.y;
  const changePct = calcMoMChange(latest.y, first.y !== 0 ? first.y : null);
  const w = 100;
  const h = 48;

  const coords = points.map((p, i) => {
    const cx = (i / Math.max(points.length - 1, 1)) * w;
    const cy = h - ((p.y - minY) / (maxY - minY)) * h;
    return { cx, cy, label: p.label, value: p.y, raw: p.raw };
  });
  const area = `0,${h} ${coords.map((c) => `${c.cx},${c.cy}`).join(" ")} ${w},${h}`;
  const line = coords.map((c) => `${c.cx},${c.cy}`).join(" ");

  return (
    <div>
      <ChartSummaryBar
        items={[
          { label: "Current", value: fmtCompact(latest.y), hint: fmtMonthLong(latest.label) },
          {
            label: "Period change",
            value: `${change >= 0 ? "+" : ""}${fmtCompact(change)}`,
            tone: change >= 0 ? "text-status-success" : "text-status-danger",
          },
          {
            label: "Range",
            value: `${fmtCompact(minY)} – ${fmtCompact(maxY)}`,
            hint: changePct !== null ? `${changePct >= 0 ? "+" : ""}${changePct.toFixed(1)}% vs start` : undefined,
          },
        ]}
      />
      <div className="relative">
        <svg viewBox={`0 0 ${w} ${h}`} className="h-36 w-full text-chart-1">
          <m.polygon
            points={area}
            fill="currentColor"
            fillOpacity={0.12}
            stroke="none"
            initial={reduced ? false : { opacity: 0 }}
            animate={{ opacity: mounted ? 0.12 : 0 }}
            transition={appPresets.barGrow.transition}
          />
          <m.polyline
            points={line}
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            vectorEffect="non-scaling-stroke"
            initial={reduced ? false : { pathLength: 0, opacity: 0.6 }}
            animate={{
              pathLength: mounted ? 1 : 0,
              opacity: mounted ? 1 : 0.6,
            }}
            transition={{ ...appPresets.barGrow.transition, delay: 0.08 }}
          />
          {coords.map((c, i) => (
            <g key={c.label}>
              <circle
                cx={c.cx}
                cy={c.cy}
                r={hovered === i ? 2.2 : 1.2}
                fill="currentColor"
                className="motion-safe-transition cursor-pointer"
                onMouseEnter={() => setHovered(i)}
                onMouseLeave={() => setHovered(null)}
              />
            </g>
          ))}
        </svg>
        {hovered !== null && coords[hovered] ? (
          <div className="absolute left-1/2 top-0 -translate-x-1/2 rounded-md bg-surface-elevated px-2 py-1 text-[10px] shadow-md">
            <span className="font-medium text-fg">{fmtMonthLong(coords[hovered].label)}</span>
            <span className="ml-1.5 tabular-nums text-fg-muted">{fmtAmount(coords[hovered].raw)}</span>
          </div>
        ) : null}
        <div className="mt-1 flex justify-between text-[9px] text-fg-muted">
          <span>{fmtMonthShort(first.label)}</span>
          <span>{fmtMonthShort(latest.label)}</span>
        </div>
      </div>
    </div>
  );
}

/** Income vs expense ratio bar for P&amp;L context */
export function PnlRatioBar({
  income,
  expense,
  netProfit,
}: {
  income: string;
  expense: string;
  netProfit: string;
}) {
  const incomeDec = parseAmount(income);
  const expenseDec = parseAmount(expense);
  const netDec = parseAmount(netProfit);
  const max = Decimal.max(incomeDec, expenseDec, new Decimal(1));
  const incomePct = incomeDec.div(max).times(100).toNumber();
  const expensePct = expenseDec.div(max).times(100).toNumber();
  const marginPct = incomeDec.gt(0) ? netDec.div(incomeDec).times(100).toNumber() : 0;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-[10px]">
        <span className="text-fg-muted">Profit margin</span>
        <span
          className={cn(
            "font-semibold tabular-nums",
            marginPct >= 0 ? "text-status-success" : "text-status-danger",
          )}
        >
          {marginPct.toFixed(1)}%
        </span>
      </div>
      <div className="space-y-1.5">
        <div className="flex items-center gap-2 text-[10px]">
          <span className="w-14 shrink-0 text-fg-muted">Income</span>
          <div className="h-2 flex-1 overflow-hidden rounded-full bg-surface-muted/50">
            <div
              className="h-full rounded-full bg-status-success/80 motion-safe-transition"
              style={{ width: `${Math.min(100, incomePct)}%` }}
            />
          </div>
          <span className="w-12 shrink-0 text-right tabular-nums text-fg">{fmtCompact(income)}</span>
        </div>
        <div className="flex items-center gap-2 text-[10px]">
          <span className="w-14 shrink-0 text-fg-muted">Expense</span>
          <div className="h-2 flex-1 overflow-hidden rounded-full bg-surface-muted/50">
            <div
              className="h-full rounded-full bg-status-warning/80 motion-safe-transition"
              style={{ width: `${Math.min(100, expensePct)}%` }}
            />
          </div>
          <span className="w-12 shrink-0 text-right tabular-nums text-fg">{fmtCompact(expense)}</span>
        </div>
      </div>
    </div>
  );
}

export function AgingStackChart({
  buckets,
  title,
}: {
  buckets: { label: string; total: string; count?: number }[];
  title?: string;
}) {
  const parsed = buckets
    .map((b) => ({ ...b, value: parseAmount(b.total).toNumber() }))
    .filter((b) => b.value > 0);
  const total = parsed.reduce((s, b) => s + b.value, 0);
  if (total <= 0) {
    return <p className="py-6 text-center text-sm text-fg-muted">No outstanding balance.</p>;
  }
  const colors = [
    "bg-status-success/80",
    "bg-chart-1",
    "bg-chart-2",
    "bg-status-warning/80",
    "bg-status-danger/80",
    "bg-chart-3",
    "bg-chart-4",
  ];
  return (
    <div>
      {title ? <p className="mb-2 text-xs font-medium text-fg-muted">{title}</p> : null}
      <div className="flex h-3 overflow-hidden rounded-full bg-surface-muted/50">
        {parsed.map((b, i) => (
          <div
            key={b.label}
            className={cn("h-full motion-safe-transition", colors[i % colors.length])}
            style={{ width: `${(b.value / total) * 100}%` }}
            title={`${b.label}: ${fmtCompact(b.value)}`}
          />
        ))}
      </div>
      <ul className="mt-3 space-y-1.5 text-xs">
        {parsed.map((b, i) => (
          <li key={b.label} className="flex items-center justify-between gap-2">
            <span className="flex items-center gap-1.5 text-fg-muted">
              <span className={cn("h-2 w-2 rounded-sm", colors[i % colors.length])} />
              {b.label}
              {b.count !== undefined ? ` (${b.count})` : ""}
            </span>
            <span className="tabular-nums font-medium text-fg">{fmtCompact(b.value)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function SalesTrendChart({
  points,
}: {
  points: { label: string; value: string }[];
}) {
  const data = points.map((p) => ({ month: p.label, totalSales: p.value }));
  return <BarChart data={data} valueKey="totalSales" labelKey="month" />;
}

export function TurnoverGauge({ ratio }: { ratio: number | null }) {
  const pct = ratio === null ? 0 : Math.min(ratio * 25, 100);
  return (
    <div className="flex flex-col items-center justify-center py-4">
      <div className="relative h-20 w-20">
        <svg viewBox="0 0 36 36" className="h-full w-full -rotate-90">
          <circle cx="18" cy="18" r="15.5" fill="none" stroke="var(--border)" strokeWidth="3" />
          <circle
            cx="18"
            cy="18"
            r="15.5"
            fill="none"
            stroke="var(--brand-600)"
            strokeWidth="3"
            strokeDasharray={`${pct} 100`}
            strokeLinecap="round"
          />
        </svg>
        <span className="absolute inset-0 flex items-center justify-center text-sm font-bold tabular-nums text-fg">
          {ratio === null ? "—" : ratio.toFixed(1)}
        </span>
      </div>
      <p className="mt-2 text-xs text-fg-muted">Turnover ratio</p>
    </div>
  );
}
