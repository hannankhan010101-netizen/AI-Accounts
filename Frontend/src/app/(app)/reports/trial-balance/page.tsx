/** Trial Balance — catalog §10 Financial */
"use client";
import { useTenantReportQuery } from "@/lib/api/tenant-query";


import { useMemo, useState } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import Decimal from "decimal.js";

import { ReportExportActions } from "@/components/reports/report-export-actions";
import { ReportAsOfPresets } from "@/components/reports/report-as-of-presets";
import { buildGridExport } from "@/lib/export/grid-export";
import { recordsToCsv } from "@/lib/export/csv";
import { Button } from "@/components/ui/button";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { useClientList } from "@/lib/hooks/use-client-list";
import { matchText } from "@/lib/list/document-list-filters";
import { useReportServerPdfExport } from "@/lib/hooks/use-report-server-pdf-export";
import { reportsApi, type TrialBalanceRow } from "@/lib/api/tenant";

function fmt(n: string): string {
  try {
    return new Decimal(n).toFixed(2);
  } catch {
    return n;
  }
}

function totals(rows: TrialBalanceRow[]): { debit: Decimal; credit: Decimal } {
  return rows.reduce(
    (acc, r) => ({
      debit: acc.debit.plus(new Decimal(r.debit || "0")),
      credit: acc.credit.plus(new Decimal(r.credit || "0")),
    }),
    { debit: new Decimal(0), credit: new Decimal(0) },
  );
}

export default function TrialBalancePage() {
  const [presetId, setPresetId] = useState<string | undefined>();
  const [draftDate, setDraftDate] = useState("");
  const [asOfDate, setAsOfDate] = useState<string | undefined>(undefined);

  const { data, isLoading, error, isFetching } = useTenantReportQuery(
    ["trial-balance", asOfDate],
    () => reportsApi.trialBalance(asOfDate ? new Date(asOfDate).toISOString() : undefined),
  );

  const rows = data?.result ?? [];
  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows,
    syncUrl: true,
    filterFn: (r, q) => matchText([r.nominalCode, r.name], q),
  });

  const grand = useMemo(() => totals(rows), [rows]);
  const diff = grand.debit.minus(grand.credit);
  const { exportPdf, exportingPdf } = useReportServerPdfExport("203", "trial-balance");

  const columns = responsiveListColumns<TrialBalanceRow>(
    [
      {
        key: "nominalCode",
        header: "Code",
        sortable: true,
        sortAccessor: (r) => r.nominalCode,
        render: (r) => (
          <Link
            href={{
              pathname: "/reports/general-ledger",
              query: { nominalCode: r.nominalCode, dateTo: asOfDate ?? "" },
            }}
            className="font-mono text-brand hover:underline"
          >
            {r.nominalCode}
          </Link>
        ),
      },
      { key: "name", header: "Account", sortable: true, sortAccessor: (r) => r.name ?? "" },
      { key: "debit", header: "Debit", align: "right", render: (r) => fmt(r.debit) },
      { key: "credit", header: "Credit", align: "right", render: (r) => fmt(r.credit) },
      {
        key: "balance",
        header: "Balance",
        align: "right",
        sortable: true,
        sortAccessor: (r) => Number(r.balance),
        render: (r) => {
          const v = new Decimal(r.balance || "0");
          return (
            <span className={v.isNegative() ? "text-status-danger" : "text-fg"}>{fmt(r.balance)}</span>
          );
        },
      },
    ],
    { primaryKey: "nominalCode", hideBelowMdKeys: ["name", "debit", "credit"] },
  );

  return (
    <div>
      <PageHeader
        title="Trial balance"
        breadcrumb="Insights / Trial balance"
        description="Debit and credit totals per nominal. Click a code to open the general ledger."
      />

      <div className="mb-4 rounded-lg border border-border bg-surface p-4">
        <ReportAsOfPresets
          activeId={presetId}
          onSelect={(id, date) => {
            setPresetId(id);
            setDraftDate(date);
            setAsOfDate(date);
          }}
        />
        <div className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-3">
          <FormField label="As of date" htmlFor="asOf">
            <Input
              id="asOf"
              type="date"
              value={draftDate}
              onChange={(e) => {
                setPresetId(undefined);
                setDraftDate(e.target.value);
              }}
            />
          </FormField>
        </div>
        <div className="mt-3 flex gap-2">
          <Button type="button" onClick={() => setAsOfDate(draftDate || undefined)}>
            Run report
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => {
              setDraftDate("");
              setAsOfDate(undefined);
              setPresetId(undefined);
              setSearch("");
            }}
          >
            Clear
          </Button>
          {isFetching && <span className="self-center text-xs text-fg-muted">Refreshing…</span>}
          <ReportExportActions
            filename="trial-balance"
            enabled={rows.length > 0}
            buildCsv={() => recordsToCsv(filtered as Record<string, unknown>[])}
            onExportPdf={() => exportPdf(asOfDate ? { dateTo: asOfDate } : {})}
            exportingPdf={exportingPdf}
          />
        </div>
      </div>

      {asOfDate && (
        <div className="mb-3">
          <Input
            type="search"
            placeholder="Filter accounts…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Filter trial balance"
          />
        </div>
      )}

      <div id="report-print-area">
        <EnterpriseGrid<TrialBalanceRow>
          columns={columns}
          layout="table"
          rows={asOfDate ? pageRows : undefined}
          loading={isLoading && Boolean(asOfDate)}
          error={error}
          emptyMessage={asOfDate ? "No journal activity for this date." : "Choose a date and run the report."}
          pagination={asOfDate ? pagination : undefined}
          virtualizeThreshold={100}
          exportCsv={
            asOfDate
              ? { ...buildGridExport("trial-balance", columns), rows: filtered }
              : undefined
          }
        />
      </div>

      {rows.length > 0 && (
        <div className="mt-3 grid grid-cols-1 gap-2 md:grid-cols-3">
          <SummaryCard label="Total debit" value={grand.debit.toFixed(2)} />
          <SummaryCard label="Total credit" value={grand.credit.toFixed(2)} />
          <SummaryCard
            label="Difference"
            value={diff.toFixed(2)}
            tone={diff.abs().lt(0.01) ? "ok" : "warn"}
          />
        </div>
      )}
    </div>
  );
}

function SummaryCard({
  label,
  value,
  tone = "neutral",
}: {
  label: string;
  value: string;
  tone?: "neutral" | "ok" | "warn";
}) {
  const toneClass =
    tone === "ok"
      ? "border-status-success/35 bg-status-success/10 text-fg"
      : tone === "warn"
        ? "alert-warning-surface border"
        : "border-border bg-surface text-fg";
  return (
    <div className={`rounded-lg border p-4 ${toneClass}`}>
      <div className="text-xs font-medium uppercase tracking-wide opacity-70">{label}</div>
      <div className="mt-1 text-lg font-semibold tabular-nums">{value}</div>
    </div>
  );
}
