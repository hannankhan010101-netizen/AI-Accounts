"use client";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export interface DateRangeValue {
  dateFrom: string;
  dateTo: string;
}

function toInputDate(d: Date): string {
  return d.toISOString().slice(0, 10);
}

export function monthStart(d: Date): Date {
  return new Date(d.getFullYear(), d.getMonth(), 1);
}

export function monthEnd(d: Date): Date {
  return new Date(d.getFullYear(), d.getMonth() + 1, 0);
}

export const reportDatePresets: { id: string; label: string; range: () => DateRangeValue }[] = [
  {
    id: "this-month",
    label: "This month",
    range: () => {
      const now = new Date();
      return { dateFrom: toInputDate(monthStart(now)), dateTo: toInputDate(now) };
    },
  },
  {
    id: "last-month",
    label: "Last month",
    range: () => {
      const now = new Date();
      const start = monthStart(new Date(now.getFullYear(), now.getMonth() - 1, 1));
      const end = monthEnd(start);
      return { dateFrom: toInputDate(start), dateTo: toInputDate(end) };
    },
  },
  {
    id: "ytd",
    label: "Year to date",
    range: () => {
      const now = new Date();
      const start = new Date(now.getFullYear(), 0, 1);
      return { dateFrom: toInputDate(start), dateTo: toInputDate(now) };
    },
  },
];

interface ReportDatePresetsProps {
  activeId?: string;
  onSelect: (presetId: string, range: DateRangeValue) => void;
  className?: string;
}

export function ReportDatePresets({ activeId, onSelect, className }: ReportDatePresetsProps) {
  return (
    <div className={cn("flex flex-wrap gap-2", className)}>
      {reportDatePresets.map((p) => (
        <Button
          key={p.id}
          type="button"
          size="sm"
          variant={activeId === p.id ? "primary" : "outline"}
          onClick={() => onSelect(p.id, p.range())}
        >
          {p.label}
        </Button>
      ))}
    </div>
  );
}
