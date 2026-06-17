"use client";

import { useEffect } from "react";

import { useTour } from "@/lib/tour/tour-context";
import { useTourProgressStore } from "@/stores/onboarding/tour-progress-store";
import { useTourUIStore } from "@/stores/onboarding/tour-ui-store";

/** Mirrors tour engine state into Zustand (read-only for analytics / FAB prefs). */
export function TourZustandBridge() {
  const {
    machine,
    progress,
    running,
    menuOpen,
    attentionPulse,
    aiPanelOpen,
    currentStep,
  } = useTour();

  const setMenuOpenZ = useTourUIStore((s) => s.setMenuOpen);
  const setAiPanelOpenZ = useTourUIStore((s) => s.setAiPanelOpen);
  const setAttentionPulseZ = useTourUIStore((s) => s.setAttentionPulse);
  const setEngineSnapshot = useTourProgressStore((s) => s.setEngineSnapshot);
  const recordStepView = useTourProgressStore((s) => s.recordStepView);

  useEffect(() => {
    setEngineSnapshot({
      machine,
      progress,
      activeTourId: running?.definition.id ?? null,
      stepIndex: running?.stepIndex ?? 0,
    });
  }, [machine, progress, running, setEngineSnapshot]);

  useEffect(() => {
    setMenuOpenZ(menuOpen);
    setAiPanelOpenZ(aiPanelOpen);
    setAttentionPulseZ(attentionPulse);
  }, [menuOpen, aiPanelOpen, attentionPulse, setMenuOpenZ, setAiPanelOpenZ, setAttentionPulseZ]);

  useEffect(() => {
    if (!running || machine !== "running" || !currentStep) return;
    recordStepView(running.stepIndex);
  }, [machine, running, currentStep, recordStepView]);

  return null;
}
