"use client";

import { ChevronDown, ChevronRight } from "lucide-react";
import { useState, type ReactNode } from "react";

import { cn } from "@/lib/utils";

export function CollapsibleReportCategory({
  title,
  count,
  defaultOpen = true,
  children,
}: {
  title: string;
  count: number;
  defaultOpen?: boolean;
  children: ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <section className="overflow-hidden rounded-lg border border-border bg-surface">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between border-b border-border px-4 py-2 text-left text-sm font-semibold surface-brand-soft hover:bg-canvas/60"
        aria-expanded={open}
      >
        <span>
          {title}
          <span className="ml-2 font-normal text-fg-muted">({count})</span>
        </span>
        {open ? (
          <ChevronDown className="h-4 w-4 shrink-0 text-fg-muted" aria-hidden />
        ) : (
          <ChevronRight className="h-4 w-4 shrink-0 text-fg-muted" aria-hidden />
        )}
      </button>
      <div className={cn(!open && "hidden")}>{children}</div>
    </section>
  );
}
