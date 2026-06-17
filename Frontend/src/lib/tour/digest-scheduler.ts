/**
 * Once-per-day auto digest when user opted in — P56.
 */

import { tourApi } from "@/lib/api/tour";
import type { ReleaseItem, UserTourProgress } from "@/lib/tour/types";
import { countUnreadReleases } from "@/lib/tour/release-feed";

function digestDayKey(companyId: string, userKey: string): string {
  const day = new Date().toISOString().slice(0, 10);
  return `fa-tour:digest:${userKey}:${companyId}:${day}`;
}

function sentDigestToday(progress: UserTourProgress): boolean {
  const at = progress.preferences?.lastDigestSentAt;
  if (!at) return false;
  return at.slice(0, 10) === new Date().toISOString().slice(0, 10);
}

export function shouldAttemptAutoDigest(
  progress: UserTourProgress,
  releases: ReleaseItem[],
): boolean {
  if (!progress.preferences?.emailDigestEnabled) return false;
  if (sentDigestToday(progress)) return false;
  return countUnreadReleases(releases, progress) > 0;
}

export async function maybeSendAutoDigest(
  companyId: string,
  userKey: string,
  progress: UserTourProgress,
  releases: ReleaseItem[],
): Promise<void> {
  if (!shouldAttemptAutoDigest(progress, releases)) return;
  const key = digestDayKey(companyId, userKey);
  if (typeof sessionStorage === "undefined") return;
  if (sessionStorage.getItem(key)) return;
  sessionStorage.setItem(key, "1");
  try {
    await tourApi.postDigestEmail();
  } catch {
    sessionStorage.removeItem(key);
  }
}
