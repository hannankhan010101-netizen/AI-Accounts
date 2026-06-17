"use client";

import { useEffect } from "react";

import { useTour } from "@/lib/tour/tour-context";
import { useCopilotStore } from "@/stores/assistant/copilot-store";

/** Sync tour learning assistant panel flag with unified AI copilot. */
export function TourCopilotBridge() {
  const { aiPanelOpen, setAiPanelOpen } = useTour();
  const open = useCopilotStore((s) => s.open);
  const setOpen = useCopilotStore((s) => s.setOpen);
  const setMode = useCopilotStore((s) => s.setMode);

  useEffect(() => {
    if (aiPanelOpen) {
      setMode("onboarding");
      setOpen(true);
    }
  }, [aiPanelOpen, setMode, setOpen]);

  useEffect(() => {
    if (!open && aiPanelOpen) {
      setAiPanelOpen(false);
    }
  }, [open, aiPanelOpen, setAiPanelOpen]);

  return null;
}
