import type { ReleaseItem, UserTourProgress } from "@/lib/tour/types";

export function releaseDismissKey(releaseId: string): string {
  return `release.${releaseId}`;
}

export function isReleaseUnread(
  release: ReleaseItem,
  progress: UserTourProgress,
): boolean {
  if (progress.dismissedHints.includes(releaseDismissKey(release.id))) {
    return false;
  }
  if (release.tourId) {
    const entry = progress.tours[release.tourId];
    if (
      entry?.status === "completed" &&
      (entry.version ?? 0) >= Number(release.version)
    ) {
      return false;
    }
  }
  return true;
}

export function countUnreadReleases(
  releases: ReleaseItem[],
  progress: UserTourProgress,
): number {
  return releases.filter((r) => isReleaseUnread(r, progress)).length;
}
