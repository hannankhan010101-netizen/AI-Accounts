"use client";

import { m } from "framer-motion";
import { ArrowRight, Lightbulb, Sparkles, X } from "lucide-react";

import { OnboardingProgressRail } from "@/components/onboarding/onboarding-progress-rail";
import { Button } from "@/components/ui/button";
import { stepCardVariants } from "@/lib/motion/onboarding-variants";
import { useReducedMotion } from "@/lib/motion/use-reduced-motion";
import { maturityLevelForScore } from "@/lib/tour/maturity";
import type { PersonaId, TourExperienceMode, TourStep } from "@/lib/tour/types";
import type { ReactNode } from "react";
import { useTourUIStore } from "@/stores/onboarding/tour-ui-store";
import { cn } from "@/lib/utils";

const PERSONA_LABEL: Record<PersonaId, string> = {
  admin: "Admin",
  accountant: "Accounting",
  sales: "Sales",
  inventory_manager: "Inventory",
  procurement: "Purchases",
  cfo: "Finance lead",
  viewer: "Viewer",
  general: "Your role",
};

type OnboardingStepCardProps = {
  step: TourStep;
  stepIndex: number;
  stepCount: number;
  tourTitle?: string;
  experienceMode?: TourExperienceMode;
  demoPreview?: ReactNode;
  persona?: PersonaId;
  maturityScore?: number;
  canAdvance: boolean;
  onNext: () => void;
  onSkipStep: () => void;
  onSkipTour: () => void;
  onDismiss: () => void;
  className?: string;
  style?: React.CSSProperties;
  compact?: boolean;
};

export function OnboardingStepCard({
  step,
  stepIndex,
  stepCount,
  tourTitle,
  experienceMode = "guided",
  demoPreview,
  persona = "general",
  maturityScore = 0,
  canAdvance,
  onNext,
  onSkipStep,
  onSkipTour,
  onDismiss,
  className,
  style,
  compact = false,
}: OnboardingStepCardProps) {
  const reduced = useReducedMotion();
  const navigating = useTourUIStore((s) => s.workflowNavigating);
  const isLast = stepIndex >= stepCount - 1;
  const level = maturityLevelForScore(maturityScore);
  const showTourTitle = !compact && stepIndex === 0 && tourTitle;

  return (
    <m.article
      role="dialog"
      aria-modal="true"
      aria-labelledby="onboarding-step-title"
      aria-describedby="onboarding-step-body"
      initial={reduced ? false : "hidden"}
      animate={reduced ? undefined : "visible"}
      exit={reduced ? undefined : "exit"}
      variants={stepCardVariants}
      className={cn(
        "onboarding-glass onboarding-gradient-border onboarding-card relative",
        compact
          ? "w-[min(19rem,calc(100vw-1.5rem))]"
          : "w-[min(22rem,calc(100vw-1.5rem))]",
        "overflow-hidden rounded-2xl",
        "max-md:fixed max-md:bottom-0 max-md:left-0 max-md:right-0 max-md:w-full max-md:rounded-b-none max-md:rounded-t-2xl",
        className,
      )}
      style={style}
    >
      <div
        className={cn(
          "onboarding-mesh border-b border-border/60",
          compact ? "px-3 pb-2 pt-3" : "px-4 pb-3 pt-4",
        )}
      >
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0 space-y-1">
            <div className="flex flex-wrap items-center gap-2">
              <span className="inline-flex items-center gap-1 rounded-full bg-brand-600/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-brand-700 dark:bg-brand-100/10 dark:text-brand-100">
                <Sparkles className="h-3 w-3" aria-hidden />
                {experienceMode === "practice"
                  ? "Practice"
                  : experienceMode === "interactive"
                    ? "Live demo"
                    : "Guided step"}
              </span>
              <span className="text-[10px] font-medium text-fg-muted">
                {PERSONA_LABEL[persona]}
              </span>
            </div>
            {showTourTitle && (
              <p className="truncate text-xs text-fg-muted">{tourTitle}</p>
            )}
            <p className="text-xs tabular-nums text-fg-muted">
              Step {stepIndex + 1} of {stepCount}
              {!compact && maturityScore > 0 && (
                <span className="ml-2">· {level.label}</span>
              )}
            </p>
          </div>
          <button
            type="button"
            onClick={onDismiss}
            className="shrink-0 rounded-lg p-1.5 text-fg-muted transition-colors hover:bg-canvas hover:text-fg focus-ring"
            aria-label="Pause guide"
          >
            <X className="h-4 w-4" aria-hidden />
          </button>
        </div>
        <OnboardingProgressRail
          stepIndex={stepIndex}
          stepCount={stepCount}
          className="mt-3"
        />
      </div>

      <div
        className={cn("space-y-2", compact ? "px-3 py-3" : "space-y-3 px-4 py-4")}
        id="onboarding-step-body"
      >
        <h2
          id="onboarding-step-title"
          className={cn(
            "font-semibold leading-snug tracking-tight text-fg",
            compact ? "text-base" : "text-lg",
          )}
        >
          {step.content.title}
        </h2>
        {step.content.why && (
          <p className="text-sm leading-relaxed text-fg-muted">{step.content.why}</p>
        )}
        <p className="text-sm leading-relaxed text-fg">{step.content.how}</p>
        {demoPreview}
        {step.content.bestPractice && (
          <div className="flex gap-2 rounded-lg border border-border/70 bg-canvas/60 px-3 py-2.5">
            <Lightbulb className="mt-0.5 h-4 w-4 shrink-0 text-brand-600 dark:text-brand-100" aria-hidden />
            <p className="text-xs leading-relaxed text-fg-muted">
              <span className="font-medium text-fg">Pro tip — </span>
              {step.content.bestPractice}
            </p>
          </div>
        )}
      </div>

      <div className="flex flex-col gap-3 border-t border-border/60 bg-canvas/30 px-4 py-3">
        <div className="flex items-center gap-2">
          <Button
            type="button"
            variant="primary"
            size="sm"
            className="min-w-[7rem] flex-1 shadow-sm"
            disabled={!canAdvance || navigating}
            onClick={onNext}
          >
            {navigating
              ? "Opening…"
              : isLast
                ? "Celebrate & finish"
                : step.enterAction?.type === "sidebarNavigate" ||
                    step.enterAction?.type === "navigate"
                  ? "Go there"
                  : step.action?.type === "navigate" ||
                      step.action?.type === "sidebarNavigate"
                    ? "Continue"
                    : step.requireTargetClick || experienceMode === "practice"
                      ? "I'll try it"
                      : "Next"}
            {!isLast && <ArrowRight className="ml-1.5 h-3.5 w-3.5" aria-hidden />}
          </Button>
        </div>
        <div className="flex flex-wrap items-center justify-between gap-x-3 gap-y-1 text-xs">
          <button
            type="button"
            className="text-fg-muted underline-offset-2 transition-colors hover:text-fg hover:underline focus-ring"
            onClick={onSkipTour}
          >
            Exit guide
          </button>
          <div className="flex items-center gap-3">
            {step.skippable !== false && !isLast && (
              <button
                type="button"
                className="text-fg-muted underline-offset-2 transition-colors hover:text-fg hover:underline focus-ring"
                onClick={onSkipStep}
              >
                Skip this step
              </button>
            )}
            <span className="hidden text-fg-muted sm:inline" aria-hidden>
              Enter · Esc
            </span>
          </div>
        </div>
      </div>
    </m.article>
  );
}
