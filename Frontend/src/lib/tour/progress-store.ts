import { normalizeTourProgress } from "@/lib/tour/normalize-progress";
import type { TourProgressEntry, UserTourProgress } from "@/lib/tour/types";

const STORAGE_VERSION = "v1";
const ACTIVE_SESSION_KEY = "fa-tour:active";

export function progressStorageKey(companyId: string, userKey: string): string {
  return `fa-tour:${STORAGE_VERSION}:${userKey}:${companyId}`;
}

export function readProgress(companyId: string, userKey: string): UserTourProgress {
  if (typeof window === "undefined") return emptyProgress();
  try {
    const raw = window.localStorage.getItem(progressStorageKey(companyId, userKey));
    if (!raw) return emptyProgress();
    const parsed = JSON.parse(raw) as UserTourProgress;
    return normalizeTourProgress({
      ...parsed,
      tours: { ...emptyProgress().tours, ...parsed.tours },
    });
  } catch {
    return emptyProgress();
  }
}

export function writeProgress(
  companyId: string,
  userKey: string,
  progress: UserTourProgress,
): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(progressStorageKey(companyId, userKey), JSON.stringify(progress));
}

export function emptyProgress(): UserTourProgress {
  return {
    tours: {},
    maturityScore: 0,
    dismissedHints: [],
    preferences: { emailDigestEnabled: false, lastDigestSentAt: null },
  };
}

export function getTourEntry(
  progress: UserTourProgress,
  tourId: string,
  version: number,
): TourProgressEntry {
  return (
    progress.tours[tourId] ?? {
      status: "not_started",
      stepIndex: 0,
      version,
    }
  );
}

export function updateTourEntry(
  progress: UserTourProgress,
  tourId: string,
  patch: Partial<TourProgressEntry>,
): UserTourProgress {
  const prev = progress.tours[tourId];
  const base: TourProgressEntry = prev ?? {
    status: "not_started",
    stepIndex: 0,
    version: patch.version ?? 1,
  };
  const next: TourProgressEntry = { ...base, ...patch };
  return {
    ...progress,
    tours: { ...progress.tours, [tourId]: next },
    lastActiveTourId: tourId,
  };
}

export function computeMaturityScore(progress: UserTourProgress): number {
  const entries = Object.values(progress.tours);
  if (entries.length === 0) return 0;
  const completed = entries.filter((e) => e.status === "completed").length;
  return Math.min(100, Math.round((completed / Math.max(entries.length, 1)) * 100));
}

export type ActiveTourSession = {
  tourId: string;
  stepIndex: number;
  startedAt: number;
};

export function readActiveSession(): ActiveTourSession | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.sessionStorage.getItem(ACTIVE_SESSION_KEY);
    if (!raw) return null;
    const s = JSON.parse(raw) as ActiveTourSession;
    if (Date.now() - s.startedAt > 30 * 60 * 1000) {
      window.sessionStorage.removeItem(ACTIVE_SESSION_KEY);
      return null;
    }
    return s;
  } catch {
    return null;
  }
}

export function writeActiveSession(session: ActiveTourSession | null): void {
  if (typeof window === "undefined") return;
  if (!session) {
    window.sessionStorage.removeItem(ACTIVE_SESSION_KEY);
    return;
  }
  window.sessionStorage.setItem(ACTIVE_SESSION_KEY, JSON.stringify(session));
}
