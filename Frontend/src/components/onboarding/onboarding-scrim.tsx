"use client";

import { m } from "framer-motion";

import { useReducedMotion } from "@/lib/motion/use-reduced-motion";
import { cn } from "@/lib/utils";

type OnboardingScrimProps = {
  variant?: "vignette" | "spotlight";
  onDismiss?: () => void;
};

/** Calm, non-blocking backdrop — click to pause optional. */
export function OnboardingScrim({ variant = "vignette", onDismiss }: OnboardingScrimProps) {
  const reduced = useReducedMotion();

  return (
    <m.div
      className={cn(
        "fixed inset-0 z-[calc(var(--z-tour)-1)]",
        variant === "vignette"
          ? "bg-[var(--onboarding-scrim)] backdrop-blur-[2px]"
          : "pointer-events-none bg-transparent",
      )}
      aria-hidden={!onDismiss}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: reduced ? 0.01 : 0.28 }}
      onClick={onDismiss}
      role={onDismiss ? "button" : undefined}
      tabIndex={onDismiss ? -1 : undefined}
      aria-label={onDismiss ? "Pause guided tour" : undefined}
    />
  );
}
