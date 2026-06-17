"use client";

import { m } from "framer-motion";

import { useReducedMotion } from "@/lib/motion/use-reduced-motion";
import { cn } from "@/lib/utils";

type OnboardingProgressRailProps = {
  stepIndex: number;
  stepCount: number;
  className?: string;
};

export function OnboardingProgressRail({
  stepIndex,
  stepCount,
  className,
}: OnboardingProgressRailProps) {
  const reduced = useReducedMotion();
  const pct = ((stepIndex + 1) / stepCount) * 100;

  return (
    <div className={cn("space-y-2", className)} aria-hidden>
      <div className="flex items-center gap-1">
        {Array.from({ length: stepCount }).map((_, i) => {
          const done = i < stepIndex;
          const current = i === stepIndex;
          return (
            <m.span
              key={i}
              className={cn(
                "h-1 flex-1 rounded-full",
                done && "bg-brand-600/70 dark:bg-brand-100/70",
                current && "bg-brand-600 dark:bg-brand-100",
                !done && !current && "bg-border",
              )}
              initial={false}
              animate={
                reduced
                  ? undefined
                  : {
                      scaleY: current ? 1.4 : 1,
                      opacity: done || current ? 1 : 0.45,
                    }
              }
              transition={{ type: "spring", stiffness: 400, damping: 28 }}
            />
          );
        })}
      </div>
      <div className="h-0.5 overflow-hidden rounded-full bg-canvas">
        <m.div
          className="h-full rounded-full bg-gradient-to-r from-brand-600/80 to-brand-600 dark:from-brand-100/80 dark:to-brand-100"
          initial={false}
          animate={{ width: `${pct}%` }}
          transition={reduced ? { duration: 0.01 } : { type: "spring", stiffness: 280, damping: 30 }}
        />
      </div>
    </div>
  );
}
