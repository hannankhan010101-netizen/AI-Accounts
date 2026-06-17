"use client";

import { memo } from "react";

import { TourOverlay } from "@/components/tour/tour-overlay";
import { TourResumeBanner } from "@/components/tour/tour-resume-banner";
import { TourCompletionToast } from "@/components/tour/tour-completion-toast";

/**
 * Tour orchestration surface — overlay, resume, completion feedback.
 * Mounted in a portal by TourRoot.
 */
export const TourEngine = memo(function TourEngine() {
  return (
    <>
      <TourResumeBanner />
      <TourCompletionToast />
      <TourOverlay />
    </>
  );
});
