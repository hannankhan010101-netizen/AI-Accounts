"use client";
import { useTenantReportQuery } from "@/lib/api/tenant-query";


import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { DynamicReportGrid } from "@/components/reports/dynamic-report-grid";
import { ReportExportActions } from "@/components/reports/report-export-actions";
import { PageHeader } from "@/components/ui/page-header";
import { dynamicRowsToCsv } from "@/lib/export/report-csv";
import { useReportServerPdfExport } from "@/lib/hooks/use-report-server-pdf-export";
import { reportsApi } from "@/lib/api/tenant";

export default function ComparativePnlPage() {
  const { exportPdf, exportingPdf } = useReportServerPdfExport(
    "209",
    "comparative-profit-and-loss",
  );
  const { data, isLoading, error } = useTenantReportQuery(["comparative-pnl"], () => reportsApi.comparativeProfitAndLoss({ periodCount: 12 }));

  const rows = data?.result ?? [];

  return (
    <div>
      <PageHeader
        title="Comparative Profit & Loss"
        breadcrumb="Insights / Comparative P&L"
        actions={
          <div className="flex flex-wrap gap-2">
            <ReportExportActions
              filename="comparative-profit-and-loss"
              enabled={rows.length > 0}
              buildCsv={() => dynamicRowsToCsv(rows)}
              onExportPdf={() => exportPdf({ periodCount: 12 })}
              exportingPdf={exportingPdf}
            />
            <Link
              href="/reports"
              className="inline-flex h-9 items-center rounded-md border border-border bg-surface px-3 text-sm font-medium text-fg hover:bg-canvas"
            >
              ← Reports
            </Link>
          </div>
        }
      />
      <div id="report-print-area">
        <DynamicReportGrid
          rows={rows}
          loading={isLoading}
          error={error}
          emptyMessage="No comparative periods returned."
        />
      </div>
    </div>
  );
}
