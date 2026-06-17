"use client";

import { AnimatePresence, m } from "framer-motion";
import type { ReactNode } from "react";

import { motionPresets } from "@/lib/motion/presets";
import { useReducedMotion } from "@/lib/motion/use-reduced-motion";
import { cn } from "@/lib/utils";

type AssistantDrawerProps = {
  open: boolean;
  onClose: () => void;
  title: ReactNode;
  headerAction?: ReactNode;
  children: ReactNode;
  className?: string;
};

export function AssistantDrawer({
  open,
  onClose,
  title,
  headerAction,
  children,
  className,
}: AssistantDrawerProps) {
  const reduced = useReducedMotion();
  const drawer = motionPresets.drawer;
  const drawerTransition = reduced
    ? { duration: 0.01 }
    : { type: "spring" as const, stiffness: 520, damping: 38, mass: 0.85 };

  return (
    <AnimatePresence>
      {open && (
        <div
          className="no-print pointer-events-none fixed inset-0 z-[calc(var(--z-tour)+3)] flex justify-end"
          role="presentation"
        >
          <m.aside
            role="dialog"
            aria-modal="false"
            aria-labelledby="onboarding-assistant-title"
            initial={reduced ? false : "hidden"}
            animate={reduced ? undefined : "visible"}
            exit={reduced ? undefined : "exit"}
            variants={drawer.variants}
            transition={drawerTransition}
            className={cn(
              "surface-glass pointer-events-auto relative flex h-full w-full max-w-sm flex-col border-l border-border-subtle bg-surface shadow-premium dark:border-l-0 dark:shadow-premium",
              "max-md:max-w-full",
              className,
            )}
          >
            <header className="onboarding-mesh flex shrink-0 items-center justify-between border-b border-border-subtle/60 px-4 py-3 dark:border-border-subtle/30">
              <div id="onboarding-assistant-title">{title}</div>
              {headerAction}
            </header>
            <div className="flex min-h-0 flex-1 flex-col overflow-hidden">{children}</div>
          </m.aside>
        </div>
      )}
    </AnimatePresence>
  );
}
