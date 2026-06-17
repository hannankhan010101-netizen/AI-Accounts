"use client";

import { ContinueBanner } from "@/components/onboarding/continue-banner";
import { useTour } from "@/lib/tour/tour-context";

export function TourResumeBanner() {
  const { resumeOffer, dismissResumeOffer, resumeFromOffer, machine } = useTour();

  if (!resumeOffer || machine !== "idle") return null;

  return (
    <ContinueBanner
      title={resumeOffer.title}
      stepIndex={resumeOffer.stepIndex}
      stepCount={resumeOffer.stepCount}
      onResume={resumeFromOffer}
      onDismiss={dismissResumeOffer}
    />
  );
}
