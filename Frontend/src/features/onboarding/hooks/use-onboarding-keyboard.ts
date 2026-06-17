"use client";

import { useEffect } from "react";

import { useTour } from "@/lib/tour/tour-context";
import { useTourUIStore } from "@/stores/onboarding/tour-ui-store";

/**
 * Global onboarding shortcuts — Alt+Shift+H menu, tour navigation when active.
 */
export function useOnboardingKeyboard() {
  const { machine, nextStep, dismissTour, setMenuOpen, menuOpen } = useTour();
  const setAiPanelOpen = useTourUIStore((s) => s.setAiPanelOpen);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      const t = e.target as HTMLElement;
      const inField =
        t.tagName === "INPUT" ||
        t.tagName === "TEXTAREA" ||
        t.tagName === "SELECT" ||
        t.isContentEditable;

      if (e.altKey && e.shiftKey && e.key.toLowerCase() === "h" && !inField) {
        e.preventDefault();
        setMenuOpen(!menuOpen);
        return;
      }

      if (e.altKey && e.shiftKey && e.key.toLowerCase() === "a" && !inField) {
        e.preventDefault();
        setAiPanelOpen(true);
        return;
      }

      const active =
        machine === "running" || machine === "waiting_target" || machine === "paused";
      if (!active || inField) return;

      if (e.key === "ArrowRight" || (e.key === "Enter" && !e.shiftKey)) {
        e.preventDefault();
        nextStep();
      }
      if (e.key === "Escape") {
        e.preventDefault();
        dismissTour();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [machine, menuOpen, nextStep, dismissTour, setMenuOpen, setAiPanelOpen]);
}
