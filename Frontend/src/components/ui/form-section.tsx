"use client";

import { cn } from "@/lib/utils";

export interface FormSectionProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
  compact?: boolean;
}

/** Grouped form block with consistent surface hierarchy. */
export function FormSection({
  title,
  description,
  children,
  className,
  compact,
}: FormSectionProps) {
  return (
    <section
      className={cn(
        "surface-elevated rounded-xl bg-surface p-4 dark:border-0",
        compact ? "space-y-3" : "space-y-4",
        className,
      )}
    >
      <div>
        <h2 className="text-label font-semibold text-fg">{title}</h2>
        {description ? <p className="mt-1 text-sm text-fg-muted">{description}</p> : null}
      </div>
      {children}
    </section>
  );
}
