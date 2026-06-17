"use client";

import { Button } from "@/components/ui/button";
import { monthEnd } from "@/components/reports/report-date-presets";
import { cn } from "@/lib/utils";

function toInputDate(d: Date): string {
  return d.toISOString().slice(0, 10);
}

const asOfPresets = [
  { id: "today", label: "Today", date: () => new Date() },
  {
    id: "month-end",
    label: "End of last month",
    date: () => monthEnd(new Date(new Date().getFullYear(), new Date().getMonth() - 1, 1)),
  },
  {
    id: "quarter-end",
    label: "End of last quarter",
    date: () => {
      const now = new Date();
      const q = Math.floor(now.getMonth() / 3);
      const endMonth = q * 3 - 1;
      return monthEnd(new Date(now.getFullYear(), endMonth, 1));
    },
  },
] as const;

interface ReportAsOfPresetsProps {
  activeId?: string;
  onSelect: (presetId: string, date: string) => void;
  className?: string;
}

export function ReportAsOfPresets({ activeId, onSelect, className }: ReportAsOfPresetsProps) {
  return (
    <div className={cn("flex flex-wrap gap-2", className)}>
      {asOfPresets.map((p) => (
        <Button
          key={p.id}
          type="button"
          size="sm"
          variant={activeId === p.id ? "primary" : "outline"}
          onClick={() => onSelect(p.id, toInputDate(p.date()))}
        >
          {p.label}
        </Button>
      ))}
    </div>
  );
}
