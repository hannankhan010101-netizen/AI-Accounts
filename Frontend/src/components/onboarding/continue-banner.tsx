"use client";

import { m } from "framer-motion";
import { Play, X } from "lucide-react";

import { OnboardingProgressRail } from "@/components/onboarding/onboarding-progress-rail";
import { Button } from "@/components/ui/button";
import { celebrationVariants } from "@/lib/motion/onboarding-variants";
import { useReducedMotion } from "@/lib/motion/use-reduced-motion";

type ContinueBannerProps = {
  title: string;
  stepIndex: number;
  stepCount: number;
  onResume: () => void;
  onDismiss: () => void;
};

export function ContinueBanner({
  title,
  stepIndex,
  stepCount,
  onResume,
  onDismiss,
}: ContinueBannerProps) {
  const reduced = useReducedMotion();

  return (
    <m.div
      role="status"
      initial={reduced ? false : "hidden"}
      animate={reduced ? undefined : "visible"}
      exit={reduced ? undefined : "exit"}
      variants={celebrationVariants}
      className="onboarding-glass onboarding-card fixed bottom-20 left-4 right-4 z-tour mx-auto max-w-md overflow-hidden rounded-2xl md:bottom-24 md:left-auto md:right-6"
    >
      <div className="flex items-start gap-3 p-4">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-600/12 dark:bg-brand-100/12">
          <Play className="h-4 w-4 text-brand-600 dark:text-brand-100" aria-hidden />
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-semibold text-fg">Continue where you left off</p>
          <p className="mt-0.5 text-sm text-fg-muted">{title}</p>
          <OnboardingProgressRail
            stepIndex={stepIndex}
            stepCount={stepCount}
            className="mt-3"
          />
        </div>
        <button
          type="button"
          onClick={onDismiss}
          className="shrink-0 rounded-lg p-1.5 text-fg-muted hover:bg-canvas focus-ring"
          aria-label="Dismiss"
        >
          <X className="h-4 w-4" aria-hidden />
        </button>
      </div>
      <div className="flex gap-2 border-t border-border/60 bg-canvas/40 px-4 py-3">
        <Button type="button" variant="primary" size="sm" className="flex-1" onClick={onResume}>
          Resume guide
        </Button>
        <Button type="button" variant="ghost" size="sm" onClick={onDismiss}>
          Later
        </Button>
      </div>
    </m.div>
  );
}
