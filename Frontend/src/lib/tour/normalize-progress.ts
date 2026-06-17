import { emptyProgress } from "@/lib/tour/progress-store";
import type { UserTourProgress } from "@/lib/tour/types";

/** Coerce API/localStorage payloads so tour UI never crashes on missing arrays. */
export function normalizeTourProgress(
  raw: Partial<UserTourProgress> | null | undefined,
): UserTourProgress {
  const base = emptyProgress();
  if (!raw || typeof raw !== "object") return base;

  const tours =
    raw.tours && typeof raw.tours === "object" && !Array.isArray(raw.tours)
      ? raw.tours
      : base.tours;

  const dismissedHints = Array.isArray(raw.dismissedHints)
    ? raw.dismissedHints.filter((h): h is string => typeof h === "string")
    : base.dismissedHints;

  const maturityScore =
    typeof raw.maturityScore === "number" && Number.isFinite(raw.maturityScore)
      ? raw.maturityScore
      : base.maturityScore;

  const preferences = {
    emailDigestEnabled: raw.preferences?.emailDigestEnabled === true,
    lastDigestSentAt:
      typeof raw.preferences?.lastDigestSentAt === "string"
        ? raw.preferences.lastDigestSentAt
        : base.preferences?.lastDigestSentAt ?? null,
  };

  return {
    tours,
    maturityScore,
    dismissedHints,
    lastActiveTourId:
      typeof raw.lastActiveTourId === "string" ? raw.lastActiveTourId : undefined,
    preferences,
  };
}
