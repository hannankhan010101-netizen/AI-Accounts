/** Analytical Reports hub — FastAccounts top-level analytical entry (catalog §10.3). */
"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { BarChart3 } from "lucide-react";


import { PageHeader } from "@/components/ui/page-header";
import { EmptyState } from "@/components/ui/empty-state";
import { InlineAlert } from "@/components/ui/inline-alert";
import { Input } from "@/components/ui/input";
import { MotionFade } from "@/components/ui/motion-fade";
import { WorkspaceLoading } from "@/components/ui/workspace-loading";
import { useTenantReportQuery } from "@/lib/api/tenant-query";
import { reportsApi } from "@/lib/api/tenant";
import { matchText } from "@/lib/list/document-list-filters";
import { reportIdHref } from "@/lib/reports/report-id-href";


export default function AnalyticalReportsPage() {
  const [search, setSearch] = useState("");

  const { data, isLoading, error } = useTenantReportQuery(["report-definitions", "analytical"], () => reportsApi.listDefinitions({ hub: "analytical" }));

  const byCategory = useMemo(() => {
    const q = search.trim().toLowerCase();
    const grouped: Record<
      string,
      { reportId: string; name: string; href: string }[]
    > = {};
    for (const row of data?.result ?? []) {
      if (q && !matchText([row.reportId, row.name, row.category], q)) continue;
      if (!grouped[row.category]) grouped[row.category] = [];
      grouped[row.category].push({
        reportId: row.reportId,
        name: row.name,
        href: reportIdHref(row.reportId, { category: row.category }),
      });
    }
    return grouped;
  }, [data?.result, search]);

  return (
    <MotionFade>
    <div>
      <PageHeader
        title="Analytical reports"
        breadcrumb="Insights / Analytical reports"
        description="Data extracts and analysis reports — separate hub as in FastAccounts."
        actions={
          <div className="flex flex-wrap gap-2">
            <Link
              href="/reports"
              className="inline-flex h-9 items-center rounded-md border border-border bg-surface px-3 text-sm font-medium text-fg hover:bg-canvas"
            >
              Standard reports
            </Link>
            <Link
              href="/reports/catalog"
              className="inline-flex h-9 items-center rounded-md border border-border bg-surface px-3 text-sm font-medium text-fg hover:bg-canvas"
            >
              Full catalog
            </Link>
          </div>
        }
      />

      <div className="mb-4 max-w-md">
        <Input
          type="search"
          placeholder="Search analytical reports…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          aria-label="Search analytical reports"
        />
      </div>

      {isLoading && <WorkspaceLoading className="mt-4" />}
      {error instanceof Error && (
        <InlineAlert variant="error" className="mt-4">
          {error.message}
        </InlineAlert>
      )}

      <div className="space-y-4">
        {Object.entries(byCategory).map(([category, items]) => (
          <section
            key={category}
            className="overflow-hidden rounded-lg border border-border bg-surface"
          >
            <div className="border-b border-border px-4 py-2 text-sm font-semibold surface-brand-soft">
              {category}
            </div>
            <ul>
              {items.map((it) => (
                <li key={it.reportId} className="border-b border-border last:border-0">
                  <div className="flex items-center justify-between gap-3 px-4 py-3 text-sm">
                    <span>
                      <span className="mr-2 font-mono text-fg-muted">{it.reportId}</span>
                      {it.name}
                    </span>
                    <Link
                      href={it.href}
                      className="shrink-0 text-sm font-medium text-brand hover:underline"
                    >
                      Open report →
                    </Link>
                  </div>
                </li>
              ))}
            </ul>
          </section>
        ))}
        {!isLoading && !error && Object.keys(byCategory).length === 0 && (
          <div className="surface-elevated rounded-xl bg-surface dark:border-0">
            <EmptyState
              icon={BarChart3}
              title={search.trim() ? "No matches" : "No analytical reports"}
              description={
                search.trim()
                  ? "Try a different search term or browse the full catalog."
                  : "Analytical report definitions will appear here when configured for your company."
              }
              action={
                search.trim() ? undefined : (
                  <Link
                    href="/reports/catalog"
                    className="text-sm font-medium text-brand hover:underline"
                  >
                    Browse full catalog →
                  </Link>
                )
              }
            />
          </div>
        )}
      </div>
    </div>
    </MotionFade>
  );
}
