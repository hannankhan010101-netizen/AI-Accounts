/** General Ledger — catalog §10 Financial */
"use client";
import { useTenantReportQuery } from "@/lib/api/tenant-query";


import Link from "next/link";
import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import Decimal from "decimal.js";

import { ReportExportActions } from "@/components/reports/report-export-actions";
import { ReportDatePresets } from "@/components/reports/report-date-presets";
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
import { reportsApi, type GeneralLedgerLine } from "@/lib/api/tenant";
import { buildJournalDetailHref } from "@/lib/reports/report-drilldown";

function fmt(n: string): string {
  try {
    return new Decimal(n).toFixed(2);
  } catch {
    return n;
  }
}

interface RunInput {
  nominalCode: string;
  dateFrom?: string;
  dateTo?: string;
}

function GeneralLedger() {
  const search = useSearchParams();
  const [presetId, setPresetId] = useState<string | undefined>();
  const [draft, setDraft] = useState<RunInput>({
    nominalCode: search.get("nominalCode") ?? "",
    dateFrom: search.get("dateFrom") ?? "",
    dateTo: search.get("dateTo") ?? "",
  });
  const [params, setParams] = useState<RunInput | null>(
    search.get("nominalCode")
      ? {
          nominalCode: search.get("nominalCode") as string,
          dateFrom: search.get("dateFrom") ?? "",
          dateTo: search.get("dateTo") ?? "",
        }
      : null,
  );

  useEffect(() => {
    const code = search.get("nominalCode");
    if (code) {
      setDraft({
        nominalCode: code,
        dateFrom: search.get("dateFrom") ?? "",
        dateTo: search.get("dateTo") ?? "",
      });
      setParams({
        nominalCode: code,
        dateFrom: search.get("dateFrom") ?? "",
        dateTo: search.get("dateTo") ?? "",
      });
    }
  }, [search]);

  const { data, isLoading, error, isFetching } = useTenantReportQuery(["general-ledger", params], () =>
      reportsApi.generalLedger({
        nominalCode: params!.nominalCode,
        dateFrom: params!.dateFrom ? new Date(params!.dateFrom).toISOString() : undefined,
        dateTo: params!.dateTo ? new Date(params!.dateTo).toISOString() : undefined,
      }),
    { enabled: !!params?.nominalCode });

  const result = data?.result;
  const lines = result?.lines ?? [];
  const { exportPdf, exportingPdf } = useReportServerPdfExport(
    "206",
    `general-ledger-${params?.nominalCode ?? "report"}`,
  );

  const { search: filterQ, setSearch: setFilterQ, pageRows, pagination, filtered } = useClientList({
    rows: lines,
    syncUrl: true,
    filterFn: (r, q) => matchText([r.journalNumber, r.refNo, r.projectCode], q),
  });

  const columns = responsiveListColumns<GeneralLedgerLine>(
    [
      {
        key: "journalNumber",
        header: "Journal",
        sortable: true,
        sortAccessor: (r) => r.journalNumber ?? "",
        render: (r) =>
          r.journalNumber ? (
            <Link href={buildJournalDetailHref(r.journalId)} className="text-brand hover:underline">
              {r.journalNumber}
            </Link>
          ) : (
            "—"
          ),
      },
      {
        key: "journalDate",
        header: "Date",
        sortable: true,
        sortAccessor: (r) => r.journalDate ?? "",
        render: (r) => (r.journalDate ? new Date(r.journalDate).toLocaleDateString() : "—"),
      },
      { key: "refNo", header: "Reference" },
      { key: "projectCode", header: "Project" },
      { key: "debit", header: "Debit", align: "right", render: (r) => fmt(r.debit) },
      { key: "credit", header: "Credit", align: "right", render: (r) => fmt(r.credit) },
      {
        key: "balance",
        header: "Balance",
        align: "right",
        render: (r) => fmt(r.balance),
      },
    ],
    { primaryKey: "journalNumber", hideBelowMdKeys: ["journalDate", "refNo", "projectCode", "debit", "credit"] },
  );

  return (
    <div>
      <PageHeader
        title="General ledger"
        breadcrumb="Insights / General ledger"
        description="Activity for one nominal with running balance. Drill in from trial balance."
      />

      <div className="mb-4 rounded-lg border border-border bg-surface p-4">
        <ReportDatePresets
          activeId={presetId}
          onSelect={(id, range) => {
            setPresetId(id);
            setDraft((s) => ({ ...s, dateFrom: range.dateFrom, dateTo: range.dateTo }));
          }}
        />
        <div className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-4">
          <FormField label="Nominal code" required>
            <Input
              value={draft.nominalCode}
              onChange={(e) => setDraft((s) => ({ ...s, nominalCode: e.target.value }))}
              placeholder="e.g. 1000"
            />
          </FormField>
          <FormField label="Date from">
            <Input
              type="date"
              value={draft.dateFrom ?? ""}
              onChange={(e) => {
                setPresetId(undefined);
                setDraft((s) => ({ ...s, dateFrom: e.target.value }));
              }}
            />
          </FormField>
          <FormField label="Date to">
            <Input
              type="date"
              value={draft.dateTo ?? ""}
              onChange={(e) => {
                setPresetId(undefined);
                setDraft((s) => ({ ...s, dateTo: e.target.value }));
              }}
            />
          </FormField>
        </div>
        <div className="mt-3 flex gap-2">
          <Button type="button" disabled={!draft.nominalCode} onClick={() => setParams({ ...draft })}>
            Run report
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => {
              setDraft({ nominalCode: "", dateFrom: "", dateTo: "" });
              setParams(null);
              setPresetId(undefined);
              setFilterQ("");
            }}
          >
            Clear
          </Button>
          {isFetching && <span className="self-center text-xs text-fg-muted">Refreshing…</span>}
          <ReportExportActions
            filename={`general-ledger-${params?.nominalCode ?? "report"}`}
            enabled={lines.length > 0}
            buildCsv={() => recordsToCsv(filtered as Record<string, unknown>[])}
            onExportPdf={
              params?.nominalCode
                ? () =>
                    exportPdf({
                      nominalCode: params.nominalCode,
                      ...(params.dateFrom ? { dateFrom: params.dateFrom } : {}),
                      ...(params.dateTo ? { dateTo: params.dateTo } : {}),
                    })
                : undefined
            }
            exportingPdf={exportingPdf}
          />
        </div>
      </div>

      {!params ? (
        <div className="rounded-lg border border-dashed border-border bg-surface p-8 text-center text-sm text-fg-muted">
          Enter a nominal code and run the report.
        </div>
      ) : (
        <div id="report-print-area">
          {result && (
            <div className="mb-3 grid grid-cols-2 gap-2 md:grid-cols-4">
              <SummaryCard label="Opening" value={fmt(result.openingBalance)} />
              <SummaryCard label="Period debit" value={fmt(result.periodDebit)} />
              <SummaryCard label="Period credit" value={fmt(result.periodCredit)} />
              <SummaryCard label="Closing" value={fmt(result.closingBalance)} tone="ok" />
            </div>
          )}
          <div className="mb-3">
            <Input
              type="search"
              placeholder="Filter lines…"
              value={filterQ}
              onChange={(e) => setFilterQ(e.target.value)}
              aria-label="Filter general ledger"
            />
          </div>
          <EnterpriseGrid<GeneralLedgerLine>
            columns={columns}
            rows={pageRows}
            layout="table"
            loading={isLoading}
            error={error}
            emptyMessage="No activity in this window."
            getRowId={(r, i) => `${r.journalId}-${i}`}
            pagination={pagination}
            virtualizeThreshold={100}
            exportCsv={{ ...buildGridExport("general-ledger", columns), rows: filtered }}
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
  tone?: "neutral" | "ok";
}) {
  const toneClass =
    tone === "ok"
      ? "border-status-success/30 bg-status-success/10 text-status-success"
      : "border-border bg-surface text-fg";
  return (
    <div className={`rounded-lg border p-4 ${toneClass}`}>
      <div className="text-xs font-medium uppercase tracking-wide opacity-70">{label}</div>
      <div className="mt-1 text-lg font-semibold tabular-nums">{value}</div>
    </div>
  );
}

export default function GeneralLedgerPage() {
  return (
    <Suspense fallback={null}>
      <GeneralLedger />
    </Suspense>
  );
}
