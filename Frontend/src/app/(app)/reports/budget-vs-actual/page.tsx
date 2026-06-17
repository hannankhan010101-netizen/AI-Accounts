/** Budget vs Actual — FA §9.3 / report BUDGET_VS_ACTUAL */
"use client";
import { useTenantReportQuery } from "@/lib/api/tenant-query";


import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { DynamicReportGrid } from "@/components/reports/dynamic-report-grid";
import { Input } from "@/components/ui/input";
import { ReportExportActions } from "@/components/reports/report-export-actions";
import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { Select } from "@/components/ui/select";
import { PageHeader } from "@/components/ui/page-header";
import { useReportServerPdfExport } from "@/lib/hooks/use-report-server-pdf-export";
import { budgetsApi, reportsApi } from "@/lib/api/tenant";
import { recordsToCsv } from "@/lib/export/csv";

export default function BudgetVsActualPage() {
  const [criteria, setCriteria] = useState({
    dateFrom: "",
    dateTo: "",
    budgetId: "",
  });
  const [runCriteria, setRunCriteria] = useState<typeof criteria | null>(null);

  const budgetsQuery = useTenantReportQuery(["budgets"], () => budgetsApi.list());

  const { data, isLoading, error } = useTenantReportQuery(["report", "BUDGET_VS_ACTUAL", runCriteria], () =>
      reportsApi.executeReport({
        reportId: "BUDGET_VS_ACTUAL",
        dateFrom: runCriteria!.dateFrom || undefined,
        dateTo: runCriteria!.dateTo || undefined,
        budgetId: runCriteria!.budgetId,
      }),
    { enabled: Boolean(runCriteria?.budgetId) });

  const rows = data?.result ?? [];
  const { exportPdf, exportingPdf } = useReportServerPdfExport(
    "BUDGET_VS_ACTUAL",
    "budget-vs-actual",
  );

  const budgetOptions = useMemo(
    () => budgetsQuery.data?.result ?? [],
    [budgetsQuery.data],
  );

  return (
    <div>
      <PageHeader
        title="Budget vs actual"
        breadcrumb="Insights / Budget vs actual"
        description="Compare budget lines to posted GL movement by nominal."
      />

      <div className="mb-4 rounded-lg border border-border bg-surface p-4">
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
          <FormField label="Date from">
            <Input
              type="date"
              value={criteria.dateFrom}
              onChange={(e) => setCriteria((c) => ({ ...c, dateFrom: e.target.value }))}
            />
          </FormField>
          <FormField label="Date to">
            <Input
              type="date"
              value={criteria.dateTo}
              onChange={(e) => setCriteria((c) => ({ ...c, dateTo: e.target.value }))}
            />
          </FormField>
        </div>
        <FormField label="Budget" className="mt-3 max-w-md">
          <Select
            value={criteria.budgetId}
            onChange={(e) => setCriteria((c) => ({ ...c, budgetId: e.target.value }))}
          >
            <option value="">Select budget…</option>
            {budgetOptions.map((b) => (
              <option key={b.id} value={b.id}>
                {b.name} ({b.fiscalYear})
              </option>
            ))}
          </Select>
        </FormField>
        <div className="mt-3 flex gap-2">
          <Button
            type="button"
            disabled={!criteria.budgetId}
            onClick={() => setRunCriteria({ ...criteria })}
          >
            Run report
          </Button>
          <ReportExportActions
            filename="budget-vs-actual"
            enabled={rows.length > 0}
            buildCsv={() => recordsToCsv(rows as Record<string, unknown>[])}
            exportingPdf={exportingPdf}
            onExportPdf={() =>
              runCriteria?.budgetId
                ? exportPdf({
                    budgetId: runCriteria.budgetId,
                    dateFrom: runCriteria.dateFrom || undefined,
                    dateTo: runCriteria.dateTo || undefined,
                  })
                : undefined
            }
          />
        </div>
      </div>

      <DynamicReportGrid rows={rows} loading={isLoading} error={error} />
    </div>
  );
}
