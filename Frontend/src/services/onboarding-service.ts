import { tourApi } from "@/lib/api/tour";
import { flushTourAnalyticsToServer, trackTourEvent } from "@/lib/tour/analytics";
import {
  getTourDefinition,
  listTourDefinitions,
  preloadTour,
  preloadToursForPath,
} from "@/lib/tour/registry";
import type { TourAnalyticsEventName, UserTourProgress } from "@/lib/tour/types";

/** Service facade for onboarding — UI-agnostic orchestration. */
export const onboardingService = {
  getTour: getTourDefinition,
  listTours: listTourDefinitions,
  preloadTour,
  preloadForPath: preloadToursForPath,
  fetchProgress: () => tourApi.getMe(),
  saveProgress: (progress: UserTourProgress) => tourApi.putProgress(progress),
  track(
    event: TourAnalyticsEventName,
    tourId: string,
    ctx: { pathname: string; companyId: string | null; stepId?: string; stepIndex?: number },
  ) {
    trackTourEvent({ event, tourId, ...ctx });
  },
  flushAnalytics: flushTourAnalyticsToServer,
  getSuggestions: (pathname: string) => tourApi.getSuggestions(pathname),
  askAssistant: (message: string, pathname: string) =>
    tourApi.postAssistant({ message, pathname }),
  sendDigestEmail: () => tourApi.postDigestEmail(),
};
