"use client";

import { create } from "zustand";

import type { TourMachineState, UserTourProgress } from "@/lib/tour/types";

export type TourAnalyticsSession = {
  tourId: string;
  startedAt: number;
  lastStepIndex: number;
  dropOffStepId?: string;
  completed: boolean;
};

type TourProgressState = {
  machine: TourMachineState;
  progress: UserTourProgress | null;
  activeTourId: string | null;
  stepIndex: number;
  session: TourAnalyticsSession | null;
  stepSkipCounts: Record<string, number>;
  setEngineSnapshot: (payload: {
    machine: TourMachineState;
    progress: UserTourProgress;
    activeTourId: string | null;
    stepIndex: number;
  }) => void;
  beginSession: (tourId: string, stepIndex: number) => void;
  recordStepView: (stepIndex: number) => void;
  recordStepSkip: (stepId: string) => void;
  endSession: (completed: boolean, dropOffStepId?: string) => void;
};

export const useTourProgressStore = create<TourProgressState>((set, get) => ({
  machine: "idle",
  progress: null,
  activeTourId: null,
  stepIndex: 0,
  session: null,
  stepSkipCounts: {},
  setEngineSnapshot: (payload) =>
    set({
      machine: payload.machine,
      progress: payload.progress,
      activeTourId: payload.activeTourId,
      stepIndex: payload.stepIndex,
    }),
  beginSession: (tourId, stepIndex) =>
    set({
      session: {
        tourId,
        startedAt: Date.now(),
        lastStepIndex: stepIndex,
        completed: false,
      },
    }),
  recordStepView: (stepIndex) => {
    const s = get().session;
    if (!s) return;
    set({ session: { ...s, lastStepIndex: stepIndex } });
  },
  recordStepSkip: (stepId) =>
    set((state) => ({
      stepSkipCounts: {
        ...state.stepSkipCounts,
        [stepId]: (state.stepSkipCounts[stepId] ?? 0) + 1,
      },
    })),
  endSession: (completed, dropOffStepId) => {
    const s = get().session;
    if (!s) return;
    set({
      session: {
        ...s,
        completed,
        dropOffStepId,
      },
    });
  },
}));
