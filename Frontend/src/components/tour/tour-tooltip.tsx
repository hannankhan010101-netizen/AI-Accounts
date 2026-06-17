"use client";

import { TooltipCard } from "@/components/tooltips/tooltip-card";
import type { TargetRect } from "@/lib/tour/target-resolver";
import type { PersonaId, TourExperienceMode, TourStep } from "@/lib/tour/types";

interface TourTooltipProps {
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
  panelOnly: boolean;
  onNext: () => void;
  onSkipStep: () => void;
  onSkipTour: () => void;
  onDismiss: () => void;
  tourId?: string;
}

/** Tour step card — Floating UI + premium onboarding shell. */
export function TourTooltip(props: TourTooltipProps) {
  return <TooltipCard {...props} centered={props.panelOnly || !props.targetRect} />;
}
