/** Profit & Loss — catalog §10 Financial. Categorized by CoaCategory.categoryType. */
"use client";
import { useTenantReportQuery } from "@/lib/api/tenant-query";


import Link from "next/link";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import Decimal from "decimal.js";

import { FinancialReportBlock } from "@/components/reports/financial-report-block";
import { ReportExportActions } from "@/components/reports/report-export-actions";
import { ReportDatePresets } from "@/components/reports/report-date-presets";
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

export default function ProfitAndLossPage() {
  const [presetId, setPresetId] = useState<string | undefined>();
  const [draft, setDraft] = useState({ dateFrom: "", dateTo: "" });
  const [params, setParams] = useState<{ dateFrom?: string; dateTo?: string }>({});

  const { exportPdf, exportingPdf } = useReportServerPdfExport("204", "profit-and-loss");

  const { data, isLoading, error, isFetching } = useTenantReportQuery(["pnl", params], () =>
      reportsApi.profitAndLoss({
        dateFrom: params.dateFrom ? new Date(params.dateFrom).toISOString() : undefined,
        dateTo: params.dateTo ? new Date(params.dateTo).toISOString() : undefined,
      }));

  return (
    <div>
      <PageHeader
        title="Profit & Loss"
        breadcrumb="Insights / Profit & Loss"
        description="Income − Expense for the chosen window. Each category's classification comes from CoaCategory.categoryType."
      />

      <div className="mb-4 rounded-lg border border-border bg-surface p-4">
        <ReportDatePresets
          activeId={presetId}
          className="mb-3"
          onSelect={(id, range) => {
            setPresetId(id);
            setDraft(range);
            setParams({ dateFrom: range.dateFrom, dateTo: range.dateTo });
          }}
        />
        <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
          <FormField label="Date from">
            <Input
              type="date"
              value={draft.dateFrom}
              onChange={(e) => {
                setPresetId(undefined);
                setDraft((s) => ({ ...s, dateFrom: e.target.value }));
              }}
            />
          </FormField>
          <FormField label="Date to">
            <Input
              type="date"
              value={draft.dateTo}
              onChange={(e) => {
                setPresetId(undefined);
                setDraft((s) => ({ ...s, dateTo: e.target.value }));
              }}
            />
          </FormField>
        </div>
        <div className="mt-3 flex gap-2">
          <Button
            type="button"
            onClick={() =>
              setParams({
                dateFrom: draft.dateFrom || undefined,
                dateTo: draft.dateTo || undefined,
              })
            }
          >
            Run report
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => {
              setPresetId(undefined);
              setDraft({ dateFrom: "", dateTo: "" });
              setParams({});
            }}
          >
            Clear
          </Button>
          {isFetching && <span className="self-center text-xs text-fg-muted">Refreshing…</span>}
          <ReportExportActions
            filename="profit-and-loss"
            enabled={!!data}
            buildCsv={() =>
              data
                ? financialSectionsToCsv([
                    { section: "Income", rows: data.result.income },
                    { section: "Expense", rows: data.result.expense },
                  ])
                : ""
            }
            onExportPdf={() =>
              exportPdf({
                ...(params.dateFrom ? { dateFrom: params.dateFrom } : {}),
                ...(params.dateTo ? { dateTo: params.dateTo } : {}),
              })
            }
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
        <div id="report-print-area" className="space-y-4">
          <FinancialReportBlock
            title="Income"
            rows={data.result.income}
            total={data.result.totals.income}
            tone="ok"
            showCategory
            drilldownDateFrom={params.dateFrom}
            drilldownDateTo={params.dateTo}
          />
          <FinancialReportBlock
            title="Expense"
            rows={data.result.expense}
            total={data.result.totals.expense}
            tone="warn"
            showCategory
            drilldownDateFrom={params.dateFrom}
            drilldownDateTo={params.dateTo}
          />
          <div className="rounded-lg border border-border bg-surface p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold uppercase tracking-wide text-fg-muted">
                Net Profit
              </span>
              <span
                className={`text-2xl font-semibold tabular-nums ${
                  new Decimal(data.result.totals.netProfit).isNegative()
                    ? "text-status-danger"
                    : "text-status-success"
                }`}
              >
                {fmt(data.result.totals.netProfit)}
              </span>
            </div>
          </div>
          {data.result.income.length === 0 && data.result.expense.length === 0 && (
            <div className="rounded-lg border border-dashed border-status-warning/40 bg-status-warning/10 p-4 text-sm text-status-warning">
              No Income or Expense rows. Open{" "}
              <Link href="/settings/coa" className="underline">
                Chart of Account
              </Link>{" "}
              and set each category&apos;s type to Income / Expense / Asset / Liability /
              Equity so the P&L and Balance Sheet can classify journal lines.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
