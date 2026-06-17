"use client";
import { useTenantReportQuery } from "@/lib/api/tenant-query";


import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { DynamicReportGrid } from "@/components/reports/dynamic-report-grid";
import { ReportExportActions } from "@/components/reports/report-export-actions";
import { PageHeader } from "@/components/ui/page-header";
import { dynamicRowsToCsv } from "@/lib/export/report-csv";
import { reportsApi } from "@/lib/api/tenant";

export default function GrniReportPage() {
  const { data, isLoading, error } = useTenantReportQuery(["report-grni"], () => reportsApi.grni());

  const rows = data?.result ?? [];

  return (
    <div>
      <PageHeader
        title="GRNI"
        breadcrumb="Insights / GRNI"
        description="Goods received not invoiced — open GRN value awaiting supplier bills."
        actions={
          <div className="flex flex-wrap gap-2">
            <ReportExportActions
              filename="report-grni"
              enabled={rows.length > 0}
              buildCsv={() => dynamicRowsToCsv(rows)}
            />
            <Link
              href="/reports"
              className="inline-flex h-9 items-center rounded-md border border-border bg-surface px-3 text-sm font-medium text-fg hover:bg-canvas"
            >
              ← Reports hub
            </Link>
          </div>
        }
      />
      <div id="report-print-area">
        <DynamicReportGrid rows={rows} loading={isLoading} error={error} />
      </div>
    </div>
  );
}
