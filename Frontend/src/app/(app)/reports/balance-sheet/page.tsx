/** Balance Sheet — catalog §10 Financial. Categorized by CoaCategory.categoryType. */
"use client";
import { useTenantReportQuery } from "@/lib/api/tenant-query";


import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import Decimal from "decimal.js";

import { FinancialReportBlock } from "@/components/reports/financial-report-block";
import { ReportExportActions } from "@/components/reports/report-export-actions";
import { ReportAsOfPresets } from "@/components/reports/report-as-of-presets";
import { financialSectionsToCsv } from "@/lib/export/report-csv";
import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { WorkspaceLoading } from "@/components/ui/workspace-loading";
import { useReportServerPdfExport } from "@/lib/hooks/use-report-server-pdf-export";
import { reportsApi } from "@/lib/api/tenant";

function fmt(v: string): string {
  try {
    return new Decimal(v).toFixed(2);
  } catch {
    return v;
  }
}

export default function BalanceSheetPage() {
  const [presetId, setPresetId] = useState<string | undefined>();
  const [draft, setDraft] = useState("");
  const [asOfDate, setAsOfDate] = useState<string | undefined>(undefined);

  const { exportPdf, exportingPdf } = useReportServerPdfExport("205", "balance-sheet");

  const { data, isLoading, error, isFetching } = useTenantReportQuery(
    ["balance-sheet", asOfDate],
    () => reportsApi.balanceSheet(asOfDate ? new Date(asOfDate).toISOString() : undefined),
  );

  return (
    <div>
      <PageHeader
        title="Balance Sheet"
        breadcrumb="Insights / Balance Sheet"
        description="Snapshot at as-of date. Retained earnings = Income − Expense to date."
      />

      <div className="mb-4 rounded-lg border border-border bg-surface p-4">
        <ReportAsOfPresets
          activeId={presetId}
          className="mb-3"
          onSelect={(id, date) => {
            setPresetId(id);
            setDraft(date);
            setAsOfDate(date);
          }}
        />
        <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
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
              setPresetId(undefined);
              setDraft("");
              setAsOfDate(undefined);
            }}
          >
            Clear
          </Button>
          {isFetching && <span className="self-center text-xs text-fg-muted">Refreshing…</span>}
          <ReportExportActions
            filename="balance-sheet"
            enabled={!!data}
            buildCsv={() =>
              data
                ? financialSectionsToCsv([
                    { section: "Assets", rows: data.result.assets },
                    { section: "Liabilities", rows: data.result.liabilities },
                    { section: "Equity", rows: data.result.equity },
                    { section: "Uncategorized", rows: data.result.uncategorized },
                  ])
                : ""
            }
            onExportPdf={() => exportPdf(asOfDate ? { dateTo: asOfDate } : {})}
            exportingPdf={exportingPdf}
          />
        </div>
      </div>

      {error instanceof Error ? (
        <div className="rounded-md border border-status-danger/30 bg-status-danger/10 p-3 text-sm text-status-danger">
          {error.message}
        </div>
      ) : isLoading ? (
        <WorkspaceLoading />
      ) : !data ? null : (
        <div id="report-print-area">
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <FinancialReportBlock
              title="Assets"
              rows={data.result.assets}
              total={data.result.totals.assets}
              tone="ok"
              drilldownDateTo={asOfDate}
            />
            <div className="space-y-4">
              <FinancialReportBlock
                title="Liabilities"
                rows={data.result.liabilities}
                total={data.result.totals.liabilities}
                tone="warn"
                drilldownDateTo={asOfDate}
              />
              <FinancialReportBlock
                title="Equity"
                rows={data.result.equity}
                total={data.result.totals.equity}
                tone="neutral"
                drilldownDateTo={asOfDate}
              />
              <div className="rounded-lg border border-border bg-surface p-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-fg-muted">Retained earnings (P&L to date)</span>
                  <span className="font-medium tabular-nums">
                    {fmt(data.result.totals.retainedEarnings)}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-4 grid grid-cols-1 gap-2 md:grid-cols-3">
            <Summary label="Total Assets" value={data.result.totals.assets} />
            <Summary
              label="Liabilities + Equity + RE"
              value={new Decimal(data.result.totals.liabilities)
                .plus(data.result.totals.equity)
                .plus(data.result.totals.retainedEarnings)
                .toFixed(2)}
            />
            <Summary
              label="Difference"
              value={data.result.totals.difference}
              tone={
                new Decimal(data.result.totals.difference).abs().lt("0.01") ? "ok" : "warn"
              }
            />
          </div>

          {data.result.uncategorized.length > 0 && (
            <div className="mt-4">
              <FinancialReportBlock
                title="Uncategorized nominals"
                rows={data.result.uncategorized}
                total={data.result.totals.uncategorized}
                tone="warn"
                showCategory
                drilldownDateTo={asOfDate}
              />
              <p className="mt-2 text-xs text-status-warning">
                Set each category&apos;s type in the Chart of Account so these rows fall into
                Assets / Liabilities / Equity / Income / Expense.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function Summary({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone?: "ok" | "warn";
}) {
  return (
    <div className="rounded-lg border border-border bg-surface px-4 py-3">
      <div className="text-xs font-medium uppercase tracking-wide text-fg-muted">{label}</div>
      <div
        className={`mt-1 text-lg font-semibold tabular-nums ${
          tone === "warn" ? "text-status-warning" : tone === "ok" ? "text-status-success" : "text-fg"
        }`}
      >
        {fmt(value)}
      </div>
    </div>
  );
}
