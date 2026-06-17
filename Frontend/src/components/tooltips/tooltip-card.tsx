"use client";

import {
  arrow,
  autoUpdate,
  flip,
  offset,
  shift,
  useFloating,
  type Placement,
} from "@floating-ui/react";
import { AnimatePresence } from "framer-motion";
import { useEffect, useMemo, useRef, useState } from "react";

import { OnboardingStepCard } from "@/components/onboarding/onboarding-step-card";
import type { TargetRect } from "@/lib/tour/target-resolver";
import {
  anchoredCardStyle,
  isCompactAnchoredCard,
  offsetForPlacement,
  resolveTourPlacement,
} from "@/lib/tour/placement-strategy";
import { trapFocus, announceToScreenReader } from "@/lib/tour/a11y";
import { DemoPreviewPanel } from "@/components/onboarding/demo-preview-panel";
import { StepAssistantInsight } from "@/components/onboarding/step-assistant-insight";
import { usePathname } from "next/navigation";
import type { PersonaId, TourExperienceMode, TourStep } from "@/lib/tour/types";

function virtualElementFromRect(rect: TargetRect) {
  return {
    getBoundingClientRect: () => ({
      width: rect.width,
      height: rect.height,
      x: rect.left,
      y: rect.top,
      top: rect.top,
      left: rect.left,
      right: rect.left + rect.width,
      bottom: rect.top + rect.height,
    }),
  };
}

export type TooltipCardProps = {
  step: TourStep;
  stepIndex: number;
  stepCount: number;
  tourTitle?: string;
  tourTagline?: string;
  experienceLabel?: string;
  experienceMode?: TourExperienceMode;
  persona?: PersonaId;
  maturityScore?: number;
  targetRect: TargetRect | null;
  centered: boolean;
  onNext: () => void;
  onSkipStep: () => void;
  onSkipTour: () => void;
  onDismiss: () => void;
  tourId?: string;
};

export function TooltipCard(props: TooltipCardProps) {
  const {
    step,
    stepIndex,
    stepCount,
    tourTitle,
    tourTagline,
    experienceLabel,
    experienceMode = "guided",
    persona,
    maturityScore,
    targetRect,
    centered,
    onNext,
    onSkipStep,
    onSkipTour,
    onDismiss,
    tourId = "",
  } = props;

  const pathname = usePathname();
  const cardRef = useRef<HTMLDivElement>(null);
  const arrowRef = useRef<HTMLDivElement>(null);
  const [canAdvance, setCanAdvance] = useState(!step.pauseAfterMs);

  const placement = useMemo(
    () => resolveTourPlacement(targetRect, step, centered),
    [targetRect, step, centered],
  );

  const compact = useMemo(
    () => isCompactAnchoredCard(targetRect, centered),
    [targetRect, centered],
  );

  const reference = useMemo(
    () => (targetRect && !centered ? virtualElementFromRect(targetRect) : null),
    [targetRect, centered],
  );

  const headerAnchor = anchoredCardStyle(targetRect, centered);

  const { refs, floatingStyles, middlewareData } = useFloating({
    placement: centered ? "bottom" : placement,
    strategy: "fixed",
    middleware: [
      offset(centered ? 0 : offsetForPlacement(placement, targetRect)),
      flip({
        padding: 20,
        fallbackAxisSideDirection: "end",
        fallbackPlacements: ["bottom-start", "bottom", "right", "left"],
      }),
      shift({ padding: 20, crossAxis: true }),
      ...(reference && !centered && !headerAnchor
        ? [arrow({ element: arrowRef, padding: 6 })]
        : []),
    ],
    whileElementsMounted: reference && !headerAnchor ? autoUpdate : undefined,
  });

  useEffect(() => {
    if (reference) refs.setReference(reference);
  }, [reference, refs]);

  useEffect(() => {
    if (!step.pauseAfterMs) {
      setCanAdvance(true);
      return;
    }
    setCanAdvance(false);
    const t = window.setTimeout(() => setCanAdvance(true), step.pauseAfterMs);
    return () => window.clearTimeout(t);
  }, [step.id, step.pauseAfterMs]);

  useEffect(() => {
    refs.setFloating(cardRef.current);
  });

  useEffect(() => {
    const el = cardRef.current;
    if (!el) return;
    const release = trapFocus(el);
    announceToScreenReader(
      `Step ${stepIndex + 1} of ${stepCount}: ${step.content.title}`,
    );
    return release;
  }, [step.id, stepIndex, stepCount, step.content.title]);

  const arrowData = middlewareData.arrow as
    | { x?: number; y?: number; staticSide?: "top" | "bottom" | "left" | "right" }
    | undefined;

  const positionStyle = centered
    ? {
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
      }
    : headerAnchor ?? floatingStyles;

  const showAssistant =
    experienceMode !== "guided" &&
    Boolean(
      step.content.assistantLine ||
        step.assistantPrompt ||
        tourId.startsWith("demo.") ||
        tourId.startsWith("onboard."),
    );

  return (
    <AnimatePresence mode="wait">
      <div
        key={step.id}
        ref={cardRef}
        className="fixed z-[calc(var(--z-tour)+2)] flex flex-col items-start"
        style={positionStyle}
      >
        {showAssistant && (
          <StepAssistantInsight
            step={step}
            tourId={tourId}
            tourTitle={tourTitle}
            tourTagline={tourTagline}
            experienceLabel={experienceLabel}
            experienceMode={experienceMode}
            pathname={pathname}
          />
        )}
        {headerAnchor && targetRect && (
          <div
            className="pointer-events-none absolute left-8 top-[-6px] h-2.5 w-2.5 rotate-45 border border-border/80 bg-surface border-b-0 border-r-0"
            aria-hidden
          />
        )}
        {!centered && !headerAnchor && (
          <div
            ref={arrowRef}
            className="pointer-events-none absolute h-2.5 w-2.5 rotate-45 border border-border/80 bg-surface"
            style={{
              left: arrowData?.x != null ? `${arrowData.x}px` : undefined,
              top: arrowData?.y != null ? `${arrowData.y}px` : undefined,
              right: arrowData?.staticSide === "left" ? "-5px" : undefined,
              bottom: arrowData?.staticSide === "top" ? "-5px" : undefined,
              ...(arrowData?.staticSide === "right" ? { left: "-5px" } : {}),
              ...(arrowData?.staticSide === "bottom" ? { top: "-5px" } : {}),
              borderTop: arrowData?.staticSide === "bottom" ? "none" : undefined,
              borderRight: arrowData?.staticSide === "left" ? "none" : undefined,
              borderBottom: arrowData?.staticSide === "top" ? "none" : undefined,
              borderLeft: arrowData?.staticSide === "right" ? "none" : undefined,
            }}
            aria-hidden
          />
        )}
        <OnboardingStepCard
          step={step}
          stepIndex={stepIndex}
          stepCount={stepCount}
          tourTitle={tourTitle}
          experienceMode={experienceMode}
          persona={persona}
          maturityScore={maturityScore}
          canAdvance={canAdvance}
          onNext={onNext}
          onSkipStep={onSkipStep}
          onSkipTour={onSkipTour}
          onDismiss={onDismiss}
          compact={compact}
          demoPreview={<DemoPreviewPanel previewId={step.demoPreviewId} />}
        />
      </div>
    </AnimatePresence>
  );
}
