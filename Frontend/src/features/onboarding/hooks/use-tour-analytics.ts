"use client";

import { useCallback, useMemo } from "react";
import { usePathname } from "next/navigation";

import { useCompany } from "@/lib/auth/company-context";
import {
  flushTourAnalyticsToServer,
  trackTourEvent,
  type TourAnalyticsPayload,
} from "@/lib/tour/analytics";
import type { TourAnalyticsEventName } from "@/lib/tour/types";
import { useTourProgressStore } from "@/stores/onboarding/tour-progress-store";

export function useTourAnalytics() {
  const pathname = usePathname();
  const { companyId } = useCompany();
  const session = useTourProgressStore((s) => s.session);
  const stepSkipCounts = useTourProgressStore((s) => s.stepSkipCounts);

  const track = useCallback(
    (
      event: TourAnalyticsEventName,
      tourId: string,
      extra?: Pick<TourAnalyticsPayload, "stepId" | "stepIndex" | "durationMs">,
    ) => {
      trackTourEvent({
        event,
        tourId,
        pathname,
        companyId,
        ...extra,
      });
      if (event === "tour_started") {
        useTourProgressStore.getState().beginSession(tourId, extra?.stepIndex ?? 0);
      }
      if (event === "step_skipped" && extra?.stepId) {
        useTourProgressStore.getState().recordStepSkip(extra.stepId);
      }
      if (event === "tour_completed") {
        useTourProgressStore.getState().endSession(true);
      }
      if (event === "tour_dismissed") {
        useTourProgressStore.getState().endSession(false, extra?.stepId);
      }
    },
    [pathname, companyId],
  );

  const flush = useCallback(() => flushTourAnalyticsToServer(), []);

  const dropOffStep = useMemo(
    () => session?.dropOffStepId ?? null,
    [session?.dropOffStepId],
  );

  return {
    track,
    flush,
    session,
    stepSkipCounts,
    dropOffStep,
  };
}
