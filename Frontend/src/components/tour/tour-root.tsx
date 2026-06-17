"use client";

import { createPortal } from "react-dom";
import { useEffect, useState } from "react";

import { TourCopilotBridge } from "@/features/assistant/tour-copilot-bridge";
import { UniversalTourButton } from "@/components/tour/universal-tour-button";
import { OnboardingErrorBoundary } from "@/features/onboarding/components/onboarding-error-boundary";
import { TourEngine } from "@/features/onboarding/components/tour-engine";
import { OnboardingProvider } from "@/features/onboarding";

function TourPortal({ children }: { children: React.ReactNode }) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  if (!mounted) return null;
  return createPortal(children, document.body);
}

/** App-wide onboarding shell — engine, motion, FAB, overlay, assistant. */
export function TourRoot({ children }: { children: React.ReactNode }) {
  return (
    <OnboardingProvider>
      {children}
      <TourPortal>
        <OnboardingErrorBoundary>
          <UniversalTourButton />
          <TourEngine />
          <TourCopilotBridge />
        </OnboardingErrorBoundary>
      </TourPortal>
    </OnboardingProvider>
  );
}
