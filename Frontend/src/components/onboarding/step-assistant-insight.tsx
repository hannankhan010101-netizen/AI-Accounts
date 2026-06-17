"use client";

import { FloatingTourAssistant } from "@/components/onboarding/floating-tour-assistant";
import { useStepAssistant } from "@/features/onboarding/hooks/use-step-assistant";
import type { TourExperienceMode, TourStep } from "@/lib/tour/types";

type StepAssistantInsightProps = {
  step: TourStep;
  tourId: string;
  tourTitle?: string;
  tourTagline?: string;
  experienceLabel?: string;
  experienceMode: TourExperienceMode;
  pathname: string;
};

export function StepAssistantInsight({
  step,
  tourId,
  tourTitle,
  tourTagline,
  experienceLabel,
  experienceMode,
  pathname,
}: StepAssistantInsightProps) {
  const enabled = experienceMode !== "guided";
  const { reply, engine, loading } = useStepAssistant({
    step,
    tourId,
    tourTitle,
    pathname,
    enabled,
  });

  if (!enabled && !step.content.assistantLine) return null;

  const line = loading
    ? "Thinking about the best way to explain this…"
    : (reply ?? step.content.how);

  const label =
    tourTagline ??
    experienceLabel ??
    (engine === "llm" ? "AI coach" : "Your guide");

  return (
    <FloatingTourAssistant
      line={line}
      experienceLabel={loading ? "…" : label}
    />
  );
}
