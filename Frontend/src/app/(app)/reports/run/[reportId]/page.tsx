/** Generic catalog report runner — sync execute for any report ID. */
"use client";
import { useTenantReportQuery } from "@/lib/api/tenant-query";


import Link from "next/link";
import { useMemo, useState } from "react";
import { useParams } from "next/navigation";


import { DynamicReportGrid } from "@/components/reports/dynamic-report-grid";
import { ReportCriteriaFields, type ReportCriteriaValue } from "@/components/reports/report-criteria-fields";
import { ReportDatePresets, type DateRangeValue } from "@/components/reports/report-date-presets";
import { ReportExportActions } from "@/components/reports/report-export-actions";
import { PageHeader } from "@/components/ui/page-header";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { dynamicRowsToCsv } from "@/lib/export/report-csv";
import { downloadReportServerExport } from "@/lib/export/report-server-export";
import { reportsApi } from "@/lib/api/tenant";
import { isGenericReportRunner, reportIdHref } from "@/lib/reports/report-id-href";


function defaultRange(): DateRangeValue {
  const now = new Date();
  const start = new Date(now.getFullYear(), now.getMonth(), 1);
  return {
    dateFrom: start.toISOString().slice(0, 10),
    dateTo: now.toISOString().slice(0, 10),
  };
}

export default function ReportRunPage() {
  const params = useParams<{ reportId: string }>();
  const reportId = decodeURIComponent(params.reportId);
  const [range, setRange] = useState<DateRangeValue>(() => defaultRange());
  const [criteria, setCriteria] = useState<Omit<ReportCriteriaValue, "dateFrom" | "dateTo">>({});
  const [presetId, setPresetId] = useState<string | undefined>("this-month");
  const [runKey, setRunKey] = useState(0);
  const [exportingPdf, setExportingPdf] = useState(false);

  const exportCriteria = useMemo(
    () => ({
      dateFrom: range.dateFrom,
      dateTo: range.dateTo,
      ...(criteria.customerId ? { customerId: criteria.customerId } : {}),
      ...(criteria.supplierId ? { supplierId: criteria.supplierId } : {}),
      ...(criteria.productCode ? { productCode: criteria.productCode } : {}),
      ...(criteria.status ? { status: criteria.status } : {}),
    }),
    [range.dateFrom, range.dateTo, criteria],
  );

  async function exportPdfServer() {
    setExportingPdf(true);
    try {
      const res = await reportsApi.exportReportSync({
        reportId,
        criteria: exportCriteria,
        format: "pdf",
      });
      downloadReportServerExport(`report-${reportId}`, res.result);
    } finally {
      setExportingPdf(false);
    }
  }

  const definitionsQuery = useTenantReportQuery(["report-definitions", "all"], () => reportsApi.listDefinitions());

  const meta = useMemo(
    () => definitionsQuery.data?.result.find((r) => r.reportId === reportId),
    [definitionsQuery.data?.result, reportId],
  );

  const useRunner = isGenericReportRunner(reportId);
  const dedicatedHref = reportIdHref(reportId);

  const { data, isLoading, error, isFetching } = useTenantReportQuery(["report-execute",
      reportId,
      range.dateFrom,
      range.dateTo,
      criteria.customerId,
      criteria.supplierId,
      criteria.productCode,
      criteria.status,
      runKey,], () =>
      reportsApi.executeReport({
        reportId,
        dateFrom: range.dateFrom,
        dateTo: range.dateTo,
        customerId: criteria.customerId,
        supplierId: criteria.supplierId,
        productCode: criteria.productCode,
        status: criteria.status,
      }),
    { enabled: useRunner });

  const rows = data?.result ?? [];
  const title = meta?.name ?? `Report ${reportId}`;

  if (!useRunner) {
    return (
      <div>
        <PageHeader title={title} breadcrumb={`Insights / ${title}`} />
        <p className="mb-4 text-sm text-fg-muted">
          This report has a dedicated page.{" "}
          <Link href={dedicatedHref} className="font-medium text-brand hover:underline">
            Open dedicated view →
          </Link>
        </p>
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        title={title}
        breadcrumb={`Insights / ${title}`}
        description={
          meta?.category
            ? `${meta.category} · ID ${reportId}`
            : `Catalog report ID ${reportId}`
        }
        actions={
          <div className="flex flex-wrap gap-2">
            <ReportExportActions
              filename={`report-${reportId}`}
              enabled={rows.length > 0}
              buildCsv={() => dynamicRowsToCsv(rows)}
              onExportPdf={exportPdfServer}
              exportingPdf={exportingPdf}
            />
            <Link
              href="/reports/catalog"
              className="inline-flex h-9 items-center rounded-md border border-border bg-surface px-3 text-sm font-medium text-fg hover:bg-canvas"
            >
              ← Full catalog
            </Link>
          </div>
        }
      />

      <div className="mb-4 space-y-3 rounded-lg border border-border bg-surface p-4">
        <ReportDatePresets
          activeId={presetId}
          onSelect={(id, r) => {
            setPresetId(id);
            setRange(r);
          }}
        />
        <div className="flex flex-wrap items-end gap-3">
          <label className="text-sm">
            <span className="mb-1 block text-fg-muted">From</span>
            <Input
              type="date"
              value={range.dateFrom}
              onChange={(e) => {
                setPresetId(undefined);
                setRange((prev) => ({ ...prev, dateFrom: e.target.value }));
              }}
            />
          </label>
          <label className="text-sm">
            <span className="mb-1 block text-fg-muted">To</span>
            <Input
              type="date"
              value={range.dateTo}
              onChange={(e) => {
                setPresetId(undefined);
                setRange((prev) => ({ ...prev, dateTo: e.target.value }));
              }}
            />
          </label>
          <Button type="button" onClick={() => setRunKey((k) => k + 1)} disabled={isFetching}>
            {isFetching ? "Running…" : "Run report"}
          </Button>
        </div>
        <ReportCriteriaFields
          schema={meta?.filterSchema as Record<string, unknown> | undefined}
          value={{ ...range, ...criteria }}
          onChange={(next) => {
            setRange({ dateFrom: next.dateFrom, dateTo: next.dateTo });
            setCriteria({
              customerId: next.customerId,
              supplierId: next.supplierId,
              productCode: next.productCode,
              status: next.status,
            });
          }}
        />
      </div>

      <div id="report-print-area">
        <DynamicReportGrid
          rows={rows}
          loading={isLoading || isFetching}
          error={error}
          emptyMessage="No rows for the selected period."
          drillContext={{ dateFrom: range.dateFrom, dateTo: range.dateTo }}
        />
      </div>
    </div>
  );
}
