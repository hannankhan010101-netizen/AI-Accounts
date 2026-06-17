"use client";

import { m } from "framer-motion";

import {
  brandSolidLabelClasses,
  brandSolidPillClasses,
} from "@/lib/design-tokens/brand-surfaces";
import { useReducedMotion } from "@/lib/motion/use-reduced-motion";
import { cn } from "@/lib/utils";

export interface PillTabProps {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
  /** Shared layoutId enables sliding pill animation across siblings. */
  layoutId?: string;
  className?: string;
}

export function PillTab({
  active,
  onClick,
  children,
  layoutId = "pill-tab-indicator",
  className,
}: PillTabProps) {
  const reduced = useReducedMotion();

  return (
    <button
      type="button"
      role="tab"
      aria-selected={active}
      tabIndex={active ? 0 : -1}
      onClick={onClick}
      className={cn(
        "relative rounded px-3 py-1.5 text-sm font-medium motion-safe-transition focus-ring",
        !active && "text-fg-muted hover:bg-surface-muted hover:text-fg",
        className,
      )}
    >
      {active && !reduced ? (
        <m.span
          layoutId={layoutId}
          className={brandSolidPillClasses}
          transition={{ type: "spring", stiffness: 420, damping: 32 }}
        />
      ) : active ? (
        <span className={brandSolidPillClasses} aria-hidden />
      ) : null}
      <span className={cn(active ? brandSolidLabelClasses : "relative")}>{children}</span>
    </button>
  );
}

export interface PillTabListProps {
  children: React.ReactNode;
  className?: string;
  "aria-label"?: string;
}

export function PillTabList({ children, className, "aria-label": ariaLabel }: PillTabListProps) {
  return (
    <nav
      role="tablist"
      className={cn(
        "relative flex rounded-lg border border-border bg-surface/80 p-0.5 text-sm",
        "dark:border-transparent dark:bg-surface-muted/50 dark:shadow-inner dark:shadow-black/20",
        className,
      )}
      aria-label={ariaLabel}
    >
      {children}
    </nav>
  );
}
