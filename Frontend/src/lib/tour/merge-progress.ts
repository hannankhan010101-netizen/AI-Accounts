import { normalizeTourProgress } from "@/lib/tour/normalize-progress";
import type { TourProgressEntry, UserTourProgress } from "@/lib/tour/types";

/** Prefer the furthest completed / in-progress state per tour. */
export function mergeTourProgress(
  server: UserTourProgress,
  local: UserTourProgress,
): UserTourProgress {
  const remote = normalizeTourProgress(server);
  const mine = normalizeTourProgress(local);
  const tours: Record<string, TourProgressEntry> = { ...mine.tours };

  for (const [id, remoteEntry] of Object.entries(remote.tours)) {
    const localEntry = mine.tours[id];
    if (!localEntry) {
      tours[id] = remoteEntry;
      continue;
    }
    const rank = (e: TourProgressEntry) => {
      if (e.status === "completed") return 4;
      if (e.status === "in_progress") return 3;
      if (e.status === "skipped") return 2;
      return 1;
    };
    tours[id] = rank(remoteEntry) >= rank(localEntry) ? remoteEntry : localEntry;
    if (
      remoteEntry.status === "in_progress" &&
      localEntry.status === "in_progress" &&
      remoteEntry.stepIndex > localEntry.stepIndex
    ) {
      tours[id] = remoteEntry;
    }
  }

  return normalizeTourProgress({
    tours,
    maturityScore: Math.max(remote.maturityScore, mine.maturityScore),
    dismissedHints: [...new Set([...remote.dismissedHints, ...mine.dismissedHints])],
    lastActiveTourId: remote.lastActiveTourId ?? mine.lastActiveTourId,
    preferences: {
      emailDigestEnabled: Boolean(
        remote.preferences?.emailDigestEnabled ?? mine.preferences?.emailDigestEnabled,
      ),
      lastDigestSentAt:
        remote.preferences?.lastDigestSentAt ?? mine.preferences?.lastDigestSentAt ?? null,
    },
  });
}
