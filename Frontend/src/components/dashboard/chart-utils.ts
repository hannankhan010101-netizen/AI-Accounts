import Decimal from "decimal.js";

export function parseAmount(v: string | number): Decimal {
  try {
    return new Decimal(v);
  } catch {
    return new Decimal(0);
  }
}

export function fmtAmount(v: string): string {
  try {
    return new Decimal(v).toFixed(2);
  } catch {
    return v;
  }
}

/** Executive-friendly amounts: 1.2M, 38.2K */
export function fmtCompact(v: string | number): string {
  const d = parseAmount(typeof v === "number" ? String(v) : v);
  const sign = d.lt(0) ? "-" : "";
  const abs = d.abs();
  if (abs.gte(1_000_000_000)) return `${sign}${abs.div(1_000_000_000).toFixed(1)}B`;
  if (abs.gte(1_000_000)) return `${sign}${abs.div(1_000_000).toFixed(1)}M`;
  if (abs.gte(10_000)) return `${sign}${abs.div(1_000).toFixed(1)}K`;
  if (abs.gte(1_000)) return `${sign}${abs.div(1_000).toFixed(2)}K`;
  return `${sign}${abs.toFixed(2)}`;
}

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

export function fmtMonthShort(month: string): string {
  const parts = month.split("-");
  if (parts.length >= 2) {
    const idx = parseInt(parts[1]!, 10) - 1;
    if (idx >= 0 && idx < 12) return MONTHS[idx]!;
  }
  return month.slice(5) || month;
}

export function fmtMonthLong(month: string): string {
  const parts = month.split("-");
  if (parts.length >= 2) {
    const y = parseInt(parts[0]!, 10);
    const m = parseInt(parts[1]!, 10) - 1;
    if (!Number.isNaN(y) && m >= 0 && m < 12) {
      return new Date(y, m, 1).toLocaleString("en-US", { month: "short", year: "numeric" });
    }
  }
  return month;
}

export function calcMoMChange(current: number, previous: number | null): number | null {
  if (previous === null || previous === 0) return null;
  return ((current - previous) / Math.abs(previous)) * 100;
}

export function pctOf(part: number, total: number): number {
  if (total <= 0) return 0;
  return (part / total) * 100;
}
