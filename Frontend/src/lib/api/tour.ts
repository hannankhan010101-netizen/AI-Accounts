/**
 * Tour / onboarding API — P48.
 */
import { apiFetch } from "./client";
import { getCurrentCompanyId } from "@/lib/auth/storage";
import type {
  AiSuggestion,
  OnboardingInsights,
  OnboardingReleaseAdmin,
  ReleaseItem,
  UserTourProgress,
} from "@/lib/tour/types";

function path(suffix: string): string {
  const id = getCurrentCompanyId();
  if (!id) throw new Error("No company selected");
  return `/api/v1/companies/${id}${suffix}`;
}

export type OnboardingMeResult = {
  progress: UserTourProgress;
  roleName: string | null;
  permissions: string[];
  releases: ReleaseItem[];
};

export const tourApi = {
  getMe: (options?: { attemptDigest?: boolean }) =>
    apiFetch<{
      result: OnboardingMeResult & {
        digestAttempt?: { sent: boolean; message: string } | null;
      };
    }>(path("/me/onboarding"), {
      query: { attemptDigest: options?.attemptDigest !== false ? "true" : "false" },
    }),

  putProgress: (progress: UserTourProgress) =>
    apiFetch<{ result: { progress: UserTourProgress } }>(path("/me/onboarding"), {
      method: "PUT",
      body: {
        tours: progress.tours,
        maturityScore: progress.maturityScore,
        dismissedHints: progress.dismissedHints,
        lastActiveTourId: progress.lastActiveTourId,
        preferences: progress.preferences
          ? { emailDigestEnabled: progress.preferences.emailDigestEnabled }
          : undefined,
      },
    }),

  postDigestEmail: () =>
    apiFetch<{ result: { sent: boolean; message: string; lastDigestSentAt?: string } }>(
      path("/me/onboarding/digest-email"),
      { method: "POST", body: {} },
    ),

  postEvents: (events: Record<string, unknown>[]) =>
    apiFetch<void>(path("/me/onboarding/events"), {
      method: "POST",
      body: { events },
    }),

  getInsights: () =>
    apiFetch<{ result: OnboardingInsights }>(path("/onboarding/insights")),

  downloadInsightsCsv: async () => {
    const id = getCurrentCompanyId();
    if (!id) throw new Error("No company selected");
    const { resolveApiUrl } = await import("@/lib/api/base-url");
    const { getTokens } = await import("@/lib/auth/storage");
    const tokens = getTokens();
    const res = await fetch(
      resolveApiUrl(`/api/v1/companies/${id}/onboarding/insights/export`),
      {
      headers: tokens?.accessToken ? { Authorization: `Bearer ${tokens.accessToken}` } : {},
    });
    if (!res.ok) throw new Error(`Export failed (${res.status})`);
    return res.blob();
  },

  getSuggestions: (pathname: string) =>
    apiFetch<{
      result: { suggestions: AiSuggestion[]; pathname: string; engine: "rules" | "llm" };
    }>(path("/me/onboarding/suggestions"), { query: { pathname } }),

  postAssistant: (body: { message: string; pathname: string }) =>
    apiFetch<{
      result: { reply: string; engine: "rules" | "llm"; pathname: string };
    }>(path("/me/onboarding/assistant"), { method: "POST", body }),

  listReleases: () =>
    apiFetch<{ result: OnboardingReleaseAdmin[] }>(path("/onboarding/releases")),

  createRelease: (body: {
    releaseKey: string;
    version?: string;
    title: string;
    summary: string;
    publishedAt: string;
    tourId?: string | null;
    href?: string | null;
    permissions?: string[];
    isActive?: boolean;
    sortOrder?: number;
  }) =>
    apiFetch<{ result: OnboardingReleaseAdmin }>(path("/onboarding/releases"), {
      method: "POST",
      body,
    }),

  updateRelease: (
    dbId: string,
    body: Partial<{
      version: string;
      title: string;
      summary: string;
      publishedAt: string;
      tourId: string | null;
      href: string | null;
      permissions: string[];
      isActive: boolean;
      sortOrder: number;
    }>,
  ) =>
    apiFetch<{ result: OnboardingReleaseAdmin }>(path(`/onboarding/releases/${dbId}`), {
      method: "PUT",
      body,
    }),

  deleteRelease: (dbId: string) =>
    apiFetch<void>(path(`/onboarding/releases/${dbId}`), { method: "DELETE" }),

  listPlatformReleases: () =>
    apiFetch<{ result: OnboardingReleaseAdmin[] }>(path("/platform/onboarding/releases")),

  createPlatformRelease: (body: {
    releaseKey: string;
    version?: string;
    title: string;
    summary: string;
    publishedAt: string;
    tourId?: string | null;
    href?: string | null;
    permissions?: string[];
    isActive?: boolean;
    sortOrder?: number;
  }) =>
    apiFetch<{ result: OnboardingReleaseAdmin }>(path("/platform/onboarding/releases"), {
      method: "POST",
      body,
    }),

  deletePlatformRelease: (dbId: string) =>
    apiFetch<void>(path(`/platform/onboarding/releases/${dbId}`), { method: "DELETE" }),
};
