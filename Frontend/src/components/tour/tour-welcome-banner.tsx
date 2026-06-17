"use client";

import { useEffect, useState } from "react";
import { m } from "framer-motion";
import { ArrowRight, Sparkles, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { stepCardVariants } from "@/lib/motion/onboarding-variants";
import { useReducedMotion } from "@/lib/motion/use-reduced-motion";
import { getTourEntry } from "@/lib/tour/progress-store";
import { useTour } from "@/lib/tour/tour-context";
import { cn } from "@/lib/utils";

const DISMISS_KEY = "fa-tour:welcome-dismissed";

export function TourWelcomeBanner() {
  const { progress, startTour, machine, resumeOffer } = useTour();
  const reduced = useReducedMotion();
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    if (sessionStorage.getItem(DISMISS_KEY) === "1") setDismissed(true);
  }, []);

  const entry = getTourEntry(progress, "onboard.core", 1);
  const tourActive =
    machine === "running" || machine === "waiting_target" || machine === "paused";

  if (tourActive || resumeOffer) return null;
  if (entry.status === "completed") return null;

  function dismiss() {
    sessionStorage.setItem(DISMISS_KEY, "1");
    setDismissed(true);
  }

  if (entry.status === "in_progress") {
    const stepNum = entry.stepIndex + 1;
    return (
      <m.div
        role="status"
        initial={reduced ? false : "hidden"}
        animate={reduced ? undefined : "visible"}
        variants={stepCardVariants}
        className="onboarding-gradient-border onboarding-card overflow-hidden rounded-2xl"
        data-tour="welcome-banner"
      >
        <div className="onboarding-mesh flex flex-col gap-3 p-5 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-600/12 dark:bg-brand-100/12">
              <Sparkles className="h-5 w-5 text-brand-600 dark:text-brand-100" aria-hidden />
            </div>
            <div>
              <p className="text-sm font-semibold text-fg">Pick up your welcome guide</p>
              <p className="mt-0.5 text-sm text-fg-muted">
                Step {stepNum} of 5 — about 2 minutes left.
              </p>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              size="sm"
              variant="primary"
              onClick={() => startTour("onboard.core", entry.stepIndex)}
            >
              Continue
              <ArrowRight className="ml-1 h-3.5 w-3.5" aria-hidden />
            </Button>
            <Button
              type="button"
              size="sm"
              variant="outline"
              onClick={() => startTour("onboard.core", 0)}
            >
              Start over
            </Button>
          </div>
        </div>
      </m.div>
    );
  }

  if (dismissed) return null;

  return (
    <m.div
      role="status"
      initial={reduced ? false : "hidden"}
      animate={reduced ? undefined : "visible"}
      variants={stepCardVariants}
      className={cn(
        "onboarding-gradient-border onboarding-card overflow-hidden rounded-2xl",
      )}
      data-tour="welcome-banner"
    >
      <div className="onboarding-mesh flex items-start gap-3 p-5">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-600/12 dark:bg-brand-100/12">
          <Sparkles className="h-5 w-5 text-brand-600 dark:text-brand-100" aria-hidden />
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-semibold text-fg">A calm 3-minute orientation</p>
          <p className="mt-1 text-sm leading-relaxed text-fg-muted">
            Learn navigation, company context, and where to find help — matched to your
            permissions. Skip anytime.
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            <Button type="button" size="sm" variant="primary" onClick={() => startTour("onboard.core")}>
              Start guide
            </Button>
            <Button type="button" size="sm" variant="ghost" onClick={dismiss}>
              Not now
            </Button>
          </div>
        </div>
        <button
          type="button"
          onClick={dismiss}
          className="shrink-0 rounded-lg p-1.5 text-fg-muted hover:bg-canvas focus-ring"
          aria-label="Dismiss"
        >
          <X className="h-4 w-4" aria-hidden />
        </button>
      </div>
    </m.div>
  );
}
