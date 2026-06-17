"use client";

import type { LucideIcon } from "lucide-react";
import { Inbox } from "lucide-react";
import { m } from "framer-motion";

import { appPresets } from "@/lib/motion/app-presets";
import { useReducedMotion } from "@/lib/motion/use-reduced-motion";
import { cn } from "@/lib/utils";

export interface EmptyStateProps {
  icon?: LucideIcon;
  title?: string;
  description: string;
  action?: React.ReactNode;
  className?: string;
}

export function EmptyState({
  icon: Icon = Inbox,
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  const reduced = useReducedMotion();
  const preset = appPresets.metricEnter;

  return (
    <m.div
      role="status"
      initial={reduced ? false : "hidden"}
      animate={reduced ? undefined : "visible"}
      variants={preset.variants}
      transition={preset.transition}
      className={cn(
        "flex flex-col items-center justify-center px-6 py-12 text-center",
        className,
      )}
    >
      <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-surface-accent text-brand">
        <Icon className="h-6 w-6" aria-hidden />
      </div>
      {title ? <p className="text-label font-semibold text-fg">{title}</p> : null}
      <p className={cn("max-w-sm text-sm text-fg-muted", title && "mt-1")}>{description}</p>
      {action ? <div className="mt-4">{action}</div> : null}
    </m.div>
  );
}
