"use client";

import { useCallback } from "react";

import { DemoCursor } from "@/components/onboarding/demo-cursor";
import { PracticeGate } from "@/components/onboarding/practice-gate";
import { shouldShowDemoCursor } from "@/lib/tour/demo-engine";
import type { TargetRect } from "@/lib/tour/target-resolver";
import type { TourDefinition, TourStep } from "@/lib/tour/types";
import { resolveTourExperience } from "@/lib/tour/types";

type InteractiveTourLayerProps = {
  definition: TourDefinition;
  step: TourStep;
  targetRect: TargetRect | null;
  onPracticeClick: () => void;
};

export function InteractiveTourLayer({
  definition,
  step,
  targetRect,
  onPracticeClick,
}: InteractiveTourLayerProps) {
  const experience = resolveTourExperience(definition);
  const showCursor = shouldShowDemoCursor(definition, step);
  const practice =
    experience === "practice" || (experience === "interactive" && step.requireTargetClick);

  const handlePracticeClick = useCallback(() => {
    onPracticeClick();
  }, [onPracticeClick]);

  const tourTargetId = step.target.kind === "tour" ? step.target.id : null;

  return (
    <>
      {showCursor && <DemoCursor targetRect={targetRect} config={step.cursor} />}
      {practice && tourTargetId && (
        <PracticeGate
          rect={targetRect}
          tourTargetId={tourTargetId}
          onTargetClicked={handlePracticeClick}
        />
      )}
    </>
  );
}
