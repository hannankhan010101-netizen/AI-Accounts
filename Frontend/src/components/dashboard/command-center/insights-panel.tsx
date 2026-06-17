"use client";

import Link from "next/link";
import { AlertTriangle, CheckCircle2, Info, TrendingUp } from "lucide-react";

import type { InsightCard, InsightSeverity } from "@/components/dashboard/command-center/types/command-center";
import { Card } from "@/components/ui/card";
import { brandLinkClasses } from "@/lib/design-tokens/brand-surfaces";
import { cn } from "@/lib/utils";

const SEVERITY_STYLE: Record<
  InsightSeverity,
  { icon: typeof Info; border: string; bg: string; text: string }
> = {
  good: {
    icon: CheckCircle2,
    border: "border-status-success/30",
    bg: "bg-status-success/8",
    text: "text-status-success",
  },
  warn: {
    icon: AlertTriangle,
    border: "border-status-warning/35",
    bg: "bg-status-warning/10",
    text: "text-status-warning",
  },
  critical: {
    icon: AlertTriangle,
    border: "border-status-danger/35",
    bg: "bg-status-danger/10",
    text: "text-status-danger",
  },
  info: {
    icon: Info,
    border: "border-border",
    bg: "bg-surface-muted/40",
    text: "text-fg-muted",
  },
};

export function InsightsPanel({ insights }: { insights: InsightCard[] }) {
  if (!insights.length) {
    return <p className="py-6 text-center text-sm text-fg-muted">No insights for this period.</p>;
  }
  return (
    <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
      {insights.map((insight) => {
        const style = SEVERITY_STYLE[insight.severity] ?? SEVERITY_STYLE.info;
        const Icon = style.icon;
        return (
          <Card
            key={insight.id}
            variant="metric"
            className={cn("border p-4", style.border, style.bg)}
          >
            <div className="flex gap-3">
              <Icon className={cn("mt-0.5 h-4 w-4 shrink-0", style.text)} aria-hidden />
              <div className="min-w-0 flex-1">
                <h3 className="text-sm font-semibold text-fg">{insight.title}</h3>
                <p className="mt-1 text-xs leading-relaxed text-fg-muted">{insight.message}</p>
                <Link
                  href={insight.actionHref}
                  className={cn("mt-2 inline-flex items-center gap-1 text-xs font-medium", brandLinkClasses)}
                >
                  <TrendingUp className="h-3 w-3" aria-hidden />
                  {insight.actionLabel}
                </Link>
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  );
}
