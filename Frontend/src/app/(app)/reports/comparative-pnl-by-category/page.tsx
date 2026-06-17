"use client";
import { useTenantReportQuery } from "@/lib/api/tenant-query";


import Link from "next/link";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { PivotReportGrid } from "@/components/reports/pivot-report-grid";
import { ReportExportActions } from "@/components/reports/report-export-actions";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { useReportServerPdfExport } from "@/lib/hooks/use-report-server-pdf-export";
import { reportsApi } from "@/lib/api/tenant";

export default function ComparativePnlByCategoryPage() {
  const [exporting, setExporting] = useState(false);
  const { exportPdf, exportingPdf } = useReportServerPdfExport(
    "207",
    "comparative-pnl-by-category",
  );
  const { data, isLoading, error } = useTenantReportQuery(["comparative-pnl-category-pivot"], () => reportsApi.comparativePnlByCategoryPivot({ periodCount: 12 }));

  const pivot = data?.result;
  const periods = pivot?.periods ?? [];
  const rows = pivot?.rows ?? [];

  return (
    <div>
      <PageHeader
        title="Comparative P&L by category"
        breadcrumb="Insights / Comparative P&L by category"
        actions={
          <div className="flex flex-wrap gap-2">
            <ReportExportActions
              filename="comparative-pnl-by-category"
              enabled={rows.length > 0}
              onExportPdf={() => exportPdf({ periodCount: 12 })}
              exportingPdf={exportingPdf}
            />
            <Button
              type="button"
              variant="outline"
              disabled={exporting}
              onClick={async () => {
                setExporting(true);
                try {
                  await reportsApi.downloadComparativePnlByCategoryPivotCsv({
                    periodCount: 12,
                  });
                } finally {
                  setExporting(false);
                }
              }}
            >
              {exporting ? "Exporting…" : "Export CSV"}
            </Button>
            <Link
              href="/reports"
              className="inline-flex h-9 items-center rounded-md border border-border bg-surface px-3 text-sm font-medium text-fg hover:bg-canvas"
            >
              ← Reports
            </Link>
          </div>
        }
      />
      {error instanceof Error && (
        <p className="mb-4 rounded-md border border-status-danger/30 bg-status-danger/10 p-3 text-sm text-status-danger">
          {error.message}
        </p>
      )}
      <div id="report-print-area">
        <PivotReportGrid periods={periods} rows={rows} loading={isLoading} />
      </div>
    </div>
  );
}
