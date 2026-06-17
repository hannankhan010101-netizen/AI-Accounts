"use client";

import { AnimatePresence } from "framer-motion";
import { useEffect } from "react";

import { InteractiveTourLayer } from "@/components/onboarding/interactive-tour-layer";
import { TourNavigatingIndicator } from "@/components/onboarding/tour-navigating-indicator";
import { OnboardingScrim } from "@/components/onboarding/onboarding-scrim";
import { TourSpotlight } from "@/components/tour/tour-spotlight";
import { TourTooltip } from "@/components/tour/tour-tooltip";
import { trackTourEvent } from "@/lib/tour/analytics";
import { getExperienceLabel } from "@/lib/tour/demo-engine";
import { useTour } from "@/lib/tour/tour-context";
import { useCompany } from "@/lib/auth/company-context";
import { usePathname } from "next/navigation";

export function TourOverlay() {
  const pathname = usePathname();
  const { companyId } = useCompany();
  const {
    machine,
    running,
    currentStep,
    targetRect,
    panelOnly,
    nextStep,
    skipStep,
    skipTour,
    dismissTour,
    persona,
    progress,
    experienceMode,
  } = useTour();

  useEffect(() => {
    if (machine !== "running" && machine !== "waiting_target") return;
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") {
        e.preventDefault();
        dismissTour();
        return;
      }
      if (e.key === "Enter" && !e.shiftKey && !e.ctrlKey && !e.metaKey && !e.altKey) {
        const tag = (e.target as HTMLElement | null)?.tagName?.toLowerCase();
        if (tag === "input" || tag === "textarea" || tag === "select") return;
        e.preventDefault();
        nextStep();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [machine, dismissTour, nextStep]);

  const tourVisible =
    running &&
    currentStep &&
    (machine === "running" || machine === "waiting_target" || machine === "paused");

  const showSpotlight = !panelOnly && targetRect;

  return (
    <AnimatePresence>
      {tourVisible && (
        <div className="no-print" aria-hidden={false}>
          <TourNavigatingIndicator />
          <OnboardingScrim
            variant={showSpotlight ? "spotlight" : "vignette"}
            onDismiss={dismissTour}
          />
          {showSpotlight && <TourSpotlight rect={targetRect} />}
          {running && currentStep && experienceMode !== "guided" && (
            <InteractiveTourLayer
              definition={running.definition}
              step={currentStep}
              targetRect={targetRect}
              onPracticeClick={() => {
                trackTourEvent({
                  event: "practice_click",
                  tourId: running.definition.id,
                  stepId: currentStep.id,
                  pathname,
                  companyId,
                });
                nextStep();
              }}
            />
          )}
          <div className="pointer-events-none fixed inset-0 z-[calc(var(--z-tour)+1)]">
            <div className="pointer-events-auto">
              <TourTooltip
                step={currentStep}
                stepIndex={running.stepIndex}
                stepCount={running.steps.length}
                tourTitle={running.definition.title}
                tourTagline={running.definition.metadata.tagline}
                experienceLabel={getExperienceLabel(running.definition)}
                experienceMode={experienceMode}
                persona={persona}
                maturityScore={progress.maturityScore}
                targetRect={targetRect}
                panelOnly={panelOnly || !showSpotlight}
                onNext={nextStep}
                onSkipStep={skipStep}
                onSkipTour={skipTour}
                onDismiss={dismissTour}
                tourId={running.definition.id}
              />
            </div>
          </div>
        </div>
      )}
    </AnimatePresence>
  );
}
