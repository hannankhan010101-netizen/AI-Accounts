"use client";

import type { ReactNode } from "react";

import { MotionProvider } from "@/components/motion/motion-provider";
import { TourZustandBridge } from "@/features/onboarding/bridge/tour-zustand-bridge";
import { useOnboardingKeyboard } from "@/features/onboarding/hooks/use-onboarding-keyboard";
import { useTourPreload } from "@/features/onboarding/hooks/use-tour-preload";
import { TourProvider } from "@/lib/tour/tour-context";

function OnboardingHosts() {
  useOnboardingKeyboard();
  useTourPreload();
  return <TourZustandBridge />;
}

/**
 * Enterprise onboarding shell — motion + tour engine + Zustand bridge + preload.
 */
export function OnboardingProvider({ children }: { children: ReactNode }) {
  return (
    <MotionProvider>
      <TourProvider>
        <OnboardingHosts />
        {children}
      </TourProvider>
    </MotionProvider>
  );
}
