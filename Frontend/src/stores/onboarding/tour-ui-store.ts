"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { TourExperienceMode } from "@/lib/tour/types";

export type FabAnchor = { x: number; y: number } | null;

type TourUIState = {
  menuOpen: boolean;
  aiPanelOpen: boolean;
  attentionPulse: boolean;
  fabDraggable: boolean;
  fabAnchor: FabAnchor;
  practiceMode: boolean;
  preferredExperience: TourExperienceMode | null;
  workflowNavigating: boolean;
  setMenuOpen: (open: boolean) => void;
  setAiPanelOpen: (open: boolean) => void;
  setAttentionPulse: (on: boolean) => void;
  setFabDraggable: (on: boolean) => void;
  setFabAnchor: (anchor: FabAnchor) => void;
  resetFabPosition: () => void;
  setPracticeMode: (on: boolean) => void;
  setPreferredExperience: (mode: TourExperienceMode | null) => void;
  setWorkflowNavigating: (on: boolean) => void;
};

export const useTourUIStore = create<TourUIState>()(
  persist(
    (set) => ({
      menuOpen: false,
      aiPanelOpen: false,
      attentionPulse: false,
      fabDraggable: false,
      fabAnchor: null,
      practiceMode: false,
      preferredExperience: null,
      workflowNavigating: false,
      setMenuOpen: (open) => set({ menuOpen: open }),
      setAiPanelOpen: (open) => set({ aiPanelOpen: open }),
      setAttentionPulse: (on) => set({ attentionPulse: on }),
      setFabDraggable: (on) => set({ fabDraggable: on }),
      setFabAnchor: (anchor) => set({ fabAnchor: anchor }),
      resetFabPosition: () => set({ fabAnchor: null }),
      setPracticeMode: (on) => set({ practiceMode: on }),
      setPreferredExperience: (mode) => set({ preferredExperience: mode }),
      setWorkflowNavigating: (on) => set({ workflowNavigating: on }),
    }),
    {
      name: "fa-onboarding:ui",
      partialize: (s) => ({
        fabDraggable: s.fabDraggable,
        fabAnchor: s.fabAnchor,
        practiceMode: s.practiceMode,
        preferredExperience: s.preferredExperience,
      }),
    },
  ),
);
