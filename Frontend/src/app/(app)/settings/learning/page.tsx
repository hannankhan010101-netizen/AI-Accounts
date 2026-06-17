/**
 * Personal learning preferences and tour progress — P57.
 */
"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import Link from "next/link";
import { useEffect, useState } from "react";
import { useMutation } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { WorkspaceLoading } from "@/components/ui/workspace-loading";
import { filterTourForContext } from "@/lib/tour/filters";
import { LAZY_TOUR_LOADERS } from "@/lib/tour/lazy-registry";
import { listTourDefinitions, preloadTour } from "@/lib/tour/registry";
import { maturityLevelForScore, completedTourCount } from "@/lib/tour/maturity";
import { tourApi } from "@/lib/api/tour";
import { useTourReplay } from "@/features/onboarding/hooks/use-tour-replay";
import { useTour } from "@/lib/tour/tour-context";
import { rbacApi } from "@/lib/api/tenant";
import { hasPermission, PERM_USERS_INVITE } from "@/lib/rbac/permissions";
import { useQuery } from "@tanstack/react-query";

export default function LearningSettingsPage() {
  const { progress, updatePreferences, unreadReleaseCount, persona, permissions, startTour } =
    useTour();
  const replayTour = useTourReplay();
  const [digestMsg, setDigestMsg] = useState<string | null>(null);
  const [catalogReady, setCatalogReady] = useState(false);

  useEffect(() => {
    void Promise.all(
      Object.keys(LAZY_TOUR_LOADERS).map((id) => preloadTour(id)),
    ).then(() => setCatalogReady(true));
  }, []);

  const permsQuery = useTenantListQuery(["my-permissions"], () => rbacApi.getMyPermissions());

  const digestMut = useMutation({
    mutationFn: () => tourApi.postDigestEmail(),
    onSuccess: (res) => setDigestMsg(res.result.message),
    onError: (e) => setDigestMsg(e instanceof Error ? e.message : "Failed"),
  });

  if (permsQuery.isLoading) return <WorkspaceLoading />;

  const canAdmin = hasPermission(permsQuery.data?.result.permissions ?? [], PERM_USERS_INVITE);
  const level = maturityLevelForScore(progress.maturityScore ?? 0);
  const completed = completedTourCount(progress);
  const eligible = listTourDefinitions().filter(
    (t) => filterTourForContext(t, { persona, permissions, progress }) !== null,
  );
  const catalogLoading = !catalogReady && eligible.length <= 1;
  const emailOn = progress.preferences?.emailDigestEnabled ?? false;

  return (
    <div className="max-w-2xl space-y-6">
      <PageHeader
        title="Learning"
        breadcrumb="Settings / Learning"
        description="Guided tours, What's New email, and your progress."
        actions={
          canAdmin ? (
            <Link href="/settings/learning-insights">
              <Button variant="outline" size="sm">
                Company insights
              </Button>
            </Link>
          ) : undefined
        }
      />

      <section className="rounded-lg border border-border bg-surface p-4">
        <h2 className="text-sm font-semibold text-fg">Your progress</h2>
        <p className="mt-2 text-sm text-fg-muted">
          Level: <span className="font-medium text-fg">{level.label}</span> ·{" "}
          {completed} of {eligible.length} available tours completed · maturity{" "}
          {progress.maturityScore ?? 0}%
        </p>
        <Button
          type="button"
          className="mt-3"
          size="sm"
          variant="outline"
          onClick={() => replayTour("onboard.core")}
        >
          Replay welcome tour
        </Button>
      </section>

      <section className="rounded-lg border border-border bg-surface p-4">
        <h2 className="text-sm font-semibold text-fg">Email notifications</h2>
        <label className="mt-3 flex cursor-pointer items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={emailOn}
            onChange={(e) => updatePreferences({ emailDigestEnabled: e.target.checked })}
            className="rounded border-border"
          />
          Send What&apos;s New digest by email (once per day when unread)
        </label>
        {emailOn && unreadReleaseCount > 0 && (
          <Button
            type="button"
            className="mt-3"
            size="sm"
            variant="primary"
            disabled={digestMut.isPending}
            onClick={() => digestMut.mutate()}
          >
            {digestMut.isPending ? "Sending…" : `Email ${unreadReleaseCount} update(s) now`}
          </Button>
        )}
        {progress.preferences?.lastDigestSentAt && (
          <p className="mt-2 text-xs text-fg-muted">
            Last digest: {new Date(progress.preferences.lastDigestSentAt).toLocaleString()}
          </p>
        )}
        {digestMsg && <p className="mt-2 text-sm text-fg-muted">{digestMsg}</p>}
      </section>

      <section className="rounded-lg border border-border bg-surface p-4">
        <h2 className="text-sm font-semibold text-fg">Available tours</h2>
        {catalogLoading && (
          <p className="mt-2 text-xs text-fg-muted">Loading tour catalog…</p>
        )}
        <ul className="mt-3 space-y-2">
          {eligible.map((t) => {
            const entry = progress.tours[t.id];
            const done = entry?.status === "completed";
            return (
              <li key={t.id} className="flex items-center justify-between gap-2 text-sm">
                <span className={done ? "text-fg-muted line-through" : "text-fg"}>
                  {t.title}
                  <span className="ml-2 text-xs text-fg-muted">({t.type})</span>
                </span>
                {!done && (
                  <Button type="button" size="sm" variant="ghost" onClick={() => startTour(t.id)}>
                    Start
                  </Button>
                )}
              </li>
            );
          })}
        </ul>
      </section>
    </div>
  );
}
