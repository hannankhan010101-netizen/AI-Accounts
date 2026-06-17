import type { TourAnalyticsEventName } from "@/lib/tour/types";

export type TourAnalyticsPayload = {
  event: TourAnalyticsEventName;
  tourId: string;
  stepId?: string;
  stepIndex?: number;
  durationMs?: number;
  pathname: string;
  companyId: string | null;
  meta?: Record<string, string | number | boolean>;
};

const queue: TourAnalyticsPayload[] = [];

function syncZustandSession(payload: TourAnalyticsPayload): void {
  if (typeof window === "undefined") return;
  void import("@/stores/onboarding/tour-progress-store").then(({ useTourProgressStore }) => {
    const store = useTourProgressStore.getState();
    if (payload.event === "tour_started" || payload.event === "tour_replayed") {
      store.beginSession(payload.tourId, payload.stepIndex ?? 0);
    }
    if (payload.event === "step_skipped" && payload.stepId) {
      store.recordStepSkip(payload.stepId);
    }
    if (payload.event === "step_viewed" && payload.stepIndex !== undefined) {
      store.recordStepView(payload.stepIndex);
    }
    if (payload.event === "tour_completed") {
      store.endSession(true);
    }
    if (payload.event === "tour_dismissed") {
      store.endSession(false, payload.stepId);
    }
  });
}

/** Batch analytics — server POST + Zustand session mirror. */
export function trackTourEvent(payload: TourAnalyticsPayload): void {
  queue.push(payload);
  syncZustandSession(payload);
  if (process.env.NODE_ENV === "development") {
    console.debug("[tour]", payload.event, payload.tourId, payload.stepId ?? "");
  }
}

export function trackFeatureAdoption(
  featureId: string,
  ctx: { pathname: string; companyId: string | null; tourId?: string },
): void {
  trackTourEvent({
    event: "feature_adoption",
    tourId: ctx.tourId ?? featureId,
    pathname: ctx.pathname,
    companyId: ctx.companyId,
    meta: { featureId },
  });
}

export function flushTourAnalytics(): TourAnalyticsPayload[] {
  const batch = [...queue];
  queue.length = 0;
  return batch;
}

/** POST batched events to server (best-effort). */
export async function flushTourAnalyticsToServer(): Promise<void> {
  const batch = flushTourAnalytics();
  if (batch.length === 0) return;
  try {
    const { tourApi } = await import("@/lib/api/tour");
    await tourApi.postEvents(
      batch.map((e) => ({
        event: e.event,
        tourId: e.tourId,
        stepId: e.stepId,
        stepIndex: e.stepIndex,
        durationMs: e.durationMs,
        pathname: e.pathname,
      })),
    );
  } catch {
    /* offline — events dropped until next session */
  }
}
