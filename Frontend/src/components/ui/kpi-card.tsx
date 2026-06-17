"use client";

import { m } from "framer-motion";
import type { ReactNode } from "react";

import { AnimatedNumber } from "@/components/ui/animated-number";
import { Card } from "@/components/ui/card";
import { appPresets } from "@/lib/motion/app-presets";
import { useReducedMotion } from "@/lib/motion/use-reduced-motion";
import { cn } from "@/lib/utils";

export interface KpiCardProps {
  label: string;
  value: string | number;
  formatValue?: (n: number) => string;
  subtitle?: string;
  delta?: string;
  deltaTone?: "positive" | "negative" | "neutral";
  href?: ReactNode;
  footer?: ReactNode;
  className?: string;
  animateValue?: boolean;
}

function parseNumeric(value: string | number): number | null {
  if (typeof value === "number") return value;
  const n = parseFloat(value.replace(/[^0-9.-]/g, ""));
  return Number.isFinite(n) ? n : null;
}

export function KpiCard({
  label,
  value,
  formatValue,
  subtitle,
  delta,
  deltaTone = "neutral",
  footer,
  className,
  animateValue = true,
}: KpiCardProps) {
  const reduced = useReducedMotion();
  const preset = appPresets.metricEnter;
  const numeric = parseNumeric(value);

  const deltaClass =
    deltaTone === "positive"
      ? "text-status-success"
      : deltaTone === "negative"
        ? "text-status-danger"
        : "text-fg-muted";

  return (
    <m.div
      initial={reduced ? false : "hidden"}
      animate={reduced ? undefined : "visible"}
      variants={preset.variants}
      transition={preset.transition}
    >
      <Card variant="metric" interactive className={cn("h-full", className)}>
        <div className="flex items-baseline justify-between gap-2">
          <p className="text-caption text-fg-muted">{label}</p>
          {subtitle ? <span className="text-xs text-fg-muted">{subtitle}</span> : null}
        </div>
        <p className="mt-2 text-2xl font-semibold tabular-nums tracking-tight text-fg">
          {animateValue && numeric !== null ? (
            <AnimatedNumber value={numeric} format={formatValue ?? ((n) => n.toFixed(2))} />
          ) : (
            value
          )}
        </p>
        {delta ? <p className={cn("mt-1 text-xs font-medium", deltaClass)}>{delta}</p> : null}
        {footer ? (
          <div className="mt-3 pt-3">
            <div className="divider-soft mb-3 dark:mb-3" aria-hidden />
            {footer}
          </div>
        ) : null}
      </Card>
    </m.div>
  );
}
