"use client";

import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export function WidgetShell({
  title,
  subtitle,
  children,
  className,
  editMode,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  className?: string;
  editMode?: boolean;
}) {
  return (
    <Card
      variant="glass"
      className={cn(
        "flex h-full flex-col p-4 surface-elevated",
        editMode && "ring-2 ring-brand-500/30 ring-offset-1 ring-offset-canvas",
        className,
      )}
    >
      <div className="mb-3 shrink-0">
        <h2 className="text-label font-semibold text-fg">{title}</h2>
        {subtitle ? <p className="mt-0.5 text-xs text-fg-muted">{subtitle}</p> : null}
      </div>
      <div className="min-h-0 flex-1 overflow-x-auto overflow-y-visible">{children}</div>
    </Card>
  );
}
