/**
 * Company tour analytics — admins with settings.users.invite (P50).
 */
"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import Link from "next/link";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { useToast } from "@/components/ui/toast";
import { WorkspaceLoading } from "@/components/ui/workspace-loading";
import { tourApi } from "@/lib/api/tour";
import { rbacApi } from "@/lib/api/tenant";
import {
  hasPermission,
  PERM_PLATFORM_PROCESS,
  PERM_USERS_INVITE,
} from "@/lib/rbac/permissions";

export default function LearningInsightsPage() {
  const toast = useToast();
  const [exporting, setExporting] = useState(false);
  const permsQuery = useTenantListQuery(["my-permissions"], () => rbacApi.getMyPermissions());
  const permissions = permsQuery.data?.result.permissions ?? [];
  const canView = hasPermission(permissions, PERM_USERS_INVITE);
  const canPlatform = hasPermission(permissions, PERM_PLATFORM_PROCESS);

  const insightsQuery = useTenantListQuery(["onboarding-insights"], () => tourApi.getInsights(),
    { enabled: canView });

  if (permsQuery.isLoading) {
    return <WorkspaceLoading />;
  }

  if (!canView) {
    return (
      <div>
        <PageHeader title="Learning insights" breadcrumb="Settings / Learning insights" />
        <p className="text-sm text-fg-muted">
          You need permission to invite users to view company onboarding analytics.
        </p>
      </div>
    );
  }

  const insights = insightsQuery.data?.result;

  return (
    <div>
      <PageHeader
        title="Learning insights"
        breadcrumb="Settings / Learning insights"
        description="Tour starts, completions, and step views aggregated from your team's activity."
        actions={
          <div className="flex gap-2">
            <Link href="/settings/onboarding-releases">
              <Button variant="outline" size="sm">
                Tenant releases
              </Button>
            </Link>
            {canPlatform && (
              <Link href="/settings/platform-releases">
                <Button variant="outline" size="sm">
                  Platform releases
                </Button>
              </Link>
            )}
            <Link href="/settings/users">
              <Button variant="outline" size="sm">
                Users
              </Button>
            </Link>
            <Button
              variant="outline"
              size="sm"
              disabled={exporting}
              onClick={async () => {
                setExporting(true);
                try {
                  const blob = await tourApi.downloadInsightsCsv();
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement("a");
                  a.href = url;
                  a.download = "learning-insights.csv";
                  a.click();
                  URL.revokeObjectURL(url);
                } catch (e) {
                  toast.error(e instanceof Error ? e.message : "Export failed");
                } finally {
                  setExporting(false);
                }
              }}
            >
              {exporting ? "Exporting…" : "Export CSV"}
            </Button>
          </div>
        }
      />

      {insightsQuery.isLoading && <WorkspaceLoading />}
      {insightsQuery.error instanceof Error && (
        <p className="text-sm text-status-danger">{insightsQuery.error.message}</p>
      )}

      {insights && (
        <div className="space-y-6">
          <section className="grid gap-4 sm:grid-cols-2">
            <StatCard label="Learners tracked" value={insights.totalLearners} />
            <StatCard label="Users with tour activity" value={insights.usersWithActivity} />
          </section>

          <section className="rounded-lg border border-border bg-surface p-4">
            <h2 className="text-sm font-semibold text-fg">Tour completion</h2>
            {insights.tourCompletion.length === 0 ? (
              <p className="mt-2 text-sm text-fg-muted">No tour events recorded yet.</p>
            ) : (
              <table className="mt-3 w-full text-sm">
                <thead>
                  <tr className="border-b border-border text-left text-xs text-fg-muted">
                    <th className="py-2 pr-4">Tour</th>
                    <th className="py-2 pr-4 text-right">Started</th>
                    <th className="py-2 pr-4 text-right">Completed</th>
                    <th className="py-2 text-right">Rate</th>
                  </tr>
                </thead>
                <tbody>
                  {insights.tourCompletion.map((row) => (
                    <tr key={row.tourId} className="border-b border-border/60">
                      <td className="py-2 pr-4 font-mono text-xs">{row.tourId}</td>
                      <td className="py-2 pr-4 text-right tabular-nums">{row.started}</td>
                      <td className="py-2 pr-4 text-right tabular-nums">{row.completed}</td>
                      <td className="py-2 text-right tabular-nums">{row.ratePercent}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>

          <section className="rounded-lg border border-border bg-surface p-4">
            <h2 className="text-sm font-semibold text-fg">Most viewed steps</h2>
            {insights.topStepViews.length === 0 ? (
              <p className="mt-2 text-sm text-fg-muted">No step views yet.</p>
            ) : (
              <ul className="mt-2 space-y-1 text-sm text-fg-muted">
                {insights.topStepViews.map((row) => (
                  <li key={row.step} className="flex justify-between gap-4">
                    <span className="font-mono text-xs text-fg">{row.step}</span>
                    <span className="tabular-nums">{row.views}</span>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border border-border bg-surface p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-fg-muted">{label}</p>
      <p className="mt-1 text-2xl font-semibold tabular-nums text-fg">{value}</p>
    </div>
  );
}
