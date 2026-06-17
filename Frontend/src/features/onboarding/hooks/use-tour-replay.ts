"use client";

import { useCallback } from "react";

import { useTour } from "@/lib/tour/tour-context";

/** Replay a tour from step 0 (analytics emitted by tour engine when previously completed). */
export function useTourReplay() {
  const { startTour } = useTour();
  return useCallback((tourId: string) => startTour(tourId, 0), [startTour]);
}
