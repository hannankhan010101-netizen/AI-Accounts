"use client";

import { create } from "zustand";

type AssistantState = {
  lastPathname: string | null;
  recentQuestions: string[];
  pinnedTourIds: string[];
  setLastPathname: (pathname: string) => void;
  pushQuestion: (q: string) => void;
  togglePinnedTour: (tourId: string) => void;
};

export const useAssistantStore = create<AssistantState>((set, get) => ({
  lastPathname: null,
  recentQuestions: [],
  pinnedTourIds: [],
  setLastPathname: (pathname) => set({ lastPathname: pathname }),
  pushQuestion: (q) => {
    const trimmed = q.trim();
    if (!trimmed) return;
    set((s) => ({
      recentQuestions: [trimmed, ...s.recentQuestions.filter((x) => x !== trimmed)].slice(0, 8),
    }));
  },
  togglePinnedTour: (tourId) => {
    const pinned = get().pinnedTourIds;
    set({
      pinnedTourIds: pinned.includes(tourId)
        ? pinned.filter((id) => id !== tourId)
        : [...pinned, tourId],
    });
  },
}));
