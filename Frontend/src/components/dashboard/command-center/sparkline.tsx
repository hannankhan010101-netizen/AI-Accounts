"use client";

import { cn } from "@/lib/utils";

export function Sparkline({
  values,
  className,
  positive,
  label = "Trend",
}: {
  values: number[];
  className?: string;
  positive?: boolean;
  label?: string;
}) {
  if (!values.length) {
    return <svg viewBox="0 0 64 20" className={cn("h-5 w-16 opacity-30", className)} aria-hidden />;
  }
  const min = Math.min(...values);
  const max = Math.max(...values, min + 1);
  const w = 64;
  const h = 20;
  const coords = values
    .map((v, i) => {
      const x = (i / Math.max(values.length - 1, 1)) * w;
      const y = h - ((v - min) / (max - min)) * h;
      return `${x},${y}`;
    })
    .join(" ");
  const stroke =
    positive === undefined
      ? "currentColor"
      : positive
        ? "var(--status-success)"
        : "var(--status-danger)";

  return (
    <svg
      viewBox={`0 0 ${w} ${h}`}
      className={cn("h-5 w-16 shrink-0", className)}
      role="img"
      aria-label={`${label}: ${values.length} data points`}
    >
      <polyline
        points={coords}
        fill="none"
        stroke={stroke}
        strokeWidth="1.5"
        vectorEffect="non-scaling-stroke"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
