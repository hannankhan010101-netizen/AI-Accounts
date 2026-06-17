/** Report catalog coverage diagnostics — P10. */
"use client";

import Link from "next/link";


import { PageHeader } from "@/components/ui/page-header";
import { WorkspaceLoading } from "@/components/ui/workspace-loading";
import { useTenantReportQuery } from "@/lib/api/tenant-query";
import { reportsApi } from "@/lib/api/tenant";


export default function ReportsCatalogPage() {
  const { data, isLoading, error } = useTenantReportQuery(["report-catalog-coverage"], () => reportsApi.catalogCoverage());

  const summary = data?.result;

  return (
    <div>
      <PageHeader
        title="Report catalog coverage"
        breadcrumb="Home / Settings / Report catalog"
        description="§10.11 registry parity — unmapped IDs should be empty after P10."
        actions={
          <Link
            href="/settings/smart"
            className="inline-flex h-9 items-center rounded-md border border-border bg-surface px-3 text-sm font-medium text-fg hover:bg-canvas"
          >
            ← Settings
          </Link>
        }
      />

      {isLoading ? <WorkspaceLoading /> : null}
      {error instanceof Error && (
        <p className="rounded-md border border-status-danger/30 bg-status-danger/10 p-3 text-sm text-status-danger">
          {error.message}
        </p>
      )}

      {summary ? (
        <section className="rounded-lg border border-border bg-surface p-4 text-sm">
          <dl className="grid grid-cols-2 gap-3 md:grid-cols-4">
            <Stat label="Catalog IDs" value={String(summary.catalogIds)} />
            <Stat label="With handler" value={String(summary.catalogWithHandler)} />
            <Stat
              label="Unmapped"
              value={String(summary.unmappedCatalogIds?.length ?? 0)}
              highlight={(summary.unmappedCatalogIds?.length ?? 0) > 0}
            />
          </dl>
          {(summary.unmappedCatalogIds?.length ?? 0) > 0 ? (
            <p className="mt-4 text-status-warning">
              Unmapped: {summary.unmappedCatalogIds.join(", ")}
            </p>
          ) : (
            <p className="mt-4 text-status-success">
              All §10.11 catalog IDs resolve to SQL handlers.
            </p>
          )}
          {"moduleReportIds" in summary && summary.moduleReportIds != null ? (
            <p className="mt-3 text-sm text-fg-muted">
              Module reports: {String(summary.moduleReportIds)} implemented · unmapped{" "}
              {(summary.unmappedModuleReportIds as string[] | undefined)?.length ?? 0}
            </p>
          ) : null}
        </section>
      ) : null}
    </div>
  );
}

function Stat({
  label,
  value,
  highlight,
}: {
  label: string;
  value: string;
  highlight?: boolean;
}) {
  return (
    <div>
      <dt className="text-xs uppercase text-fg-muted">{label}</dt>
      <dd
        className={`mt-1 text-lg font-semibold ${highlight ? "text-status-warning" : "text-fg"}`}
      >
        {value}
      </dd>
    </div>
  );
}
