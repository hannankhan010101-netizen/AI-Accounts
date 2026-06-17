"use client";
import { useTenantReportQuery } from "@/lib/api/tenant-query";


import Link from "next/link";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import Decimal from "decimal.js";

import { Button } from "@/components/ui/button";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { ReportExportActions } from "@/components/reports/report-export-actions";
import { ReportAsOfPresets } from "@/components/reports/report-as-of-presets";
import { buildGridExport } from "@/lib/export/grid-export";
import { recordsToCsv } from "@/lib/export/csv";
import { useClientList } from "@/lib/hooks/use-client-list";
import { matchText } from "@/lib/list/document-list-filters";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { useReportServerPdfExport } from "@/lib/hooks/use-report-server-pdf-export";
import { reportsApi, type AgingResult, type AgingRow } from "@/lib/api/tenant";

function fmt(v: string): string {
  try {
    return new Decimal(v).toFixed(2);
  } catch {
    return v;
  }
}

interface AgingReportProps {
  kind: "ar" | "ap";
  statementRoute: string;
}

export function AgingReport({ kind, statementRoute }: AgingReportProps) {
  const [presetId, setPresetId] = useState<string | undefined>();
  const [draft, setDraft] = useState("");
  const [asOfDate, setAsOfDate] = useState<string | undefined>(undefined);

  const { data, isLoading, error, isFetching } = useTenantReportQuery(["aging", kind, asOfDate], () => {
    const iso = asOfDate ? new Date(asOfDate).toISOString() : undefined;
    return kind === "ar" ? reportsApi.arAging(iso) : reportsApi.apAging(iso);
  });

  const result: AgingResult | undefined = data?.result;
  const partyParam = kind === "ar" ? "customerId" : "supplierId";
  const reportId = kind === "ar" ? "AR_AGING" : "AP_AGING";
  const { exportPdf, exportingPdf } = useReportServerPdfExport(
    reportId,
    kind === "ar" ? "ar-aging" : "ap-aging",
  );

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows: result?.rows,
    syncUrl: true,
    filterFn: (r, q) => matchText([r.partyCode, r.partyName, r.bucket], q),
  });

  const columns = responsiveListColumns<AgingRow>([
    { key: "partyCode", header: "Code" },
    {
      key: "partyName",
      header: kind === "ar" ? "Customer" : "Supplier",
      render: (r) => (
        <Link
          href={{ pathname: statementRoute, query: { [partyParam]: r.partyId } }}
          className="text-brand hover:underline"
        >
          {r.partyName ?? r.partyId.slice(0, 8)}
        </Link>
      ),
    },
    { key: "bucket", header: "Bucket" },
    { key: "ageDays", header: "Age", align: "right" },
    {
      key: "invoicesTotal",
      header: kind === "ar" ? "Invoiced" : "Billed",
      align: "right",
      render: (r) => fmt(r.invoicesTotal),
    },
    {
      key: "receiptsTotal",
      header: kind === "ar" ? "Received" : "Paid",
      align: "right",
      render: (r) => fmt(r.receiptsTotal),
    },
    {
      key: "balance",
      header: "Balance",
      align: "right",
      render: (r) => {
        const v = new Decimal(r.balance);
        return (
          <span className={v.isNegative() ? "text-status-success" : "text-fg"}>
            {fmt(r.balance)}
          </span>
        );
      },
    },
  ]);

  return (
    <>
      <div className="mb-4 rounded-lg border border-border bg-surface p-4">
        <ReportAsOfPresets
          activeId={presetId}
          onSelect={(id, date) => {
            setPresetId(id);
            setDraft(date);
            setAsOfDate(date);
          }}
        />
        <div className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-3">
          <FormField label="As of date">
            <Input
              type="date"
              value={draft}
              onChange={(e) => {
                setPresetId(undefined);
                setDraft(e.target.value);
              }}
            />
          </FormField>
        </div>
        <div className="mt-3 flex gap-2">
          <Button type="button" onClick={() => setAsOfDate(draft || undefined)}>
            Run report
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => {
              setDraft("");
              setAsOfDate(undefined);
              setPresetId(undefined);
              setSearch("");
            }}
          >
            Clear
          </Button>
          {isFetching && <span className="self-center text-xs text-fg-muted">Refreshing…</span>}
          <ReportExportActions
            filename={kind === "ar" ? "ar-aging" : "ap-aging"}
            enabled={!!result}
            buildCsv={() => recordsToCsv((result?.rows ?? filtered) as Record<string, unknown>[])}
            exportingPdf={exportingPdf}
            onExportPdf={() =>
              exportPdf(
                asOfDate
                  ? { asOfDate, dateTo: asOfDate }
                  : {},
              )
            }
          />
        </div>
      </div>

      <div id="report-print-area">
      {result && (
        <div className="mb-4 grid grid-cols-2 gap-2 md:grid-cols-4 lg:grid-cols-7">
          {result.buckets.map((b) => (
            <div
              key={b.label}
              className="rounded-lg border border-border bg-surface p-3"
            >
              <div className="text-xs font-medium uppercase tracking-wide text-fg-muted">
                {b.label}
              </div>
              <div className="mt-1 text-sm font-semibold tabular-nums text-fg">
                {fmt(b.total)}
              </div>
              <div className="text-xs text-fg-muted">{b.count} parties</div>
            </div>
          ))}
        </div>
      )}

      {result && (
        <div className="mb-3 rounded-lg border border-brand-200 p-4 surface-brand-soft dark:border-brand-400/30">
          <div className="flex items-center justify-between">
            <span className="text-sm font-semibold uppercase tracking-wide">
              {kind === "ar" ? "Total receivable" : "Total payable"}
            </span>
            <span className="text-2xl font-semibold tabular-nums text-brand-900 dark:text-brand-200">
              {fmt(result.totals.outstanding)}
            </span>
          </div>
          <div className="mt-1 text-xs">
            {result.totals.partyCount}{" "}
            {kind === "ar" ? "customers" : "suppliers"} with open balance · as of{" "}
            {result.asOfDate}
          </div>
        </div>
      )}

      {asOfDate && (
        <div className="mb-3">
          <Input
            type="search"
            placeholder={`Filter ${kind === "ar" ? "customers" : "suppliers"}…`}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      )}
      <EnterpriseGrid<AgingRow>
        columns={columns}
        rows={asOfDate ? pageRows : undefined}
        loading={isLoading}
        error={error}
        emptyMessage="No open balances."
        getRowId={(r) => r.partyId}
        pagination={asOfDate ? pagination : undefined}
        exportCsv={
          asOfDate
            ? { ...buildGridExport(kind === "ar" ? "ar-aging" : "ap-aging", columns), rows: filtered }
            : undefined
        }
      />
      </div>
    </>
  );
}
