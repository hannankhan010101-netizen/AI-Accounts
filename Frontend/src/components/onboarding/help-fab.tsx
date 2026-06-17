"use client";

import { m } from "framer-motion";
import { BookOpen } from "lucide-react";

import { useReducedMotion } from "@/lib/motion/use-reduced-motion";
import { cn } from "@/lib/utils";

type HelpFabProps = {
  active?: boolean;
  stepBadge?: number;
  unreadCount?: number;
  expanded?: boolean;
  onClick: () => void;
  className?: string;
};

/** Calm learning entry — not a loud chat bubble. */
export function HelpFab({
  active,
  stepBadge,
  unreadCount,
  expanded,
  onClick,
  className,
}: HelpFabProps) {
  const reduced = useReducedMotion();

  return (
    <m.button
      type="button"
      onClick={onClick}
      aria-label={active ? "Exit guided tour" : "Open learning hub"}
      aria-expanded={expanded}
      aria-haspopup="menu"
      whileHover={reduced ? undefined : { scale: 1.02 }}
      whileTap={reduced ? undefined : { scale: 0.98 }}
      className={cn(
        "group relative flex items-center gap-0 overflow-hidden rounded-full",
        "onboarding-glass onboarding-card border border-border/80 shadow-lg",
        "transition-[padding] duration-200 ease-out focus-ring",
        active ? "bg-brand-600/8 pr-3 dark:bg-brand-100/8" : "hover:pr-3",
        className,
      )}
    >
      {!reduced && !active && (
        <m.span
          className="pointer-events-none absolute -inset-1 rounded-full opacity-40"
          style={{
            background:
              "radial-gradient(circle, var(--onboarding-glow) 0%, transparent 70%)",
          }}
          animate={{ opacity: [0.25, 0.45, 0.25] }}
          transition={{ duration: 3.5, repeat: Infinity, ease: "easeInOut" }}
          aria-hidden
        />
      )}
      <span
        className={cn(
          "flex h-11 w-11 shrink-0 items-center justify-center rounded-full",
          active && "ring-2 ring-brand-600/30 dark:ring-brand-100/30",
        )}
      >
        <BookOpen
          className={cn(
            "h-5 w-5 transition-colors",
            active ? "text-brand-700 dark:text-brand-100" : "text-brand-600 dark:text-brand-100",
          )}
          aria-hidden
        />
      </span>
      <span
        className={cn(
          "max-w-0 overflow-hidden whitespace-nowrap text-sm font-medium text-fg opacity-0",
          "transition-all duration-200 group-hover:max-w-[5rem] group-hover:opacity-100",
          expanded && "max-w-[5rem] opacity-100",
        )}
      >
        Learn
      </span>
      {active && stepBadge !== undefined && (
        <span className="absolute -right-0.5 -top-0.5 flex h-5 min-w-5 items-center justify-center rounded-full px-1 text-[10px] font-semibold btn-brand">
          {stepBadge}
        </span>
      )}
      {!active && unreadCount !== undefined && unreadCount > 0 && (
        <span className="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-status-warning px-1 text-[10px] font-medium text-on-brand">
          {unreadCount > 9 ? "9+" : unreadCount}
        </span>
      )}
    </m.button>
  );
}
