"use client";

import Link from "next/link";
import Decimal from "decimal.js";

import { useMemo } from "react";

import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { buildGeneralLedgerHref } from "@/lib/reports/report-drilldown";
import { cn } from "@/lib/utils";

export interface FinancialReportRow {
  nominalCode: string;
  name?: string | null;
  categoryName?: string;
  amount: string;
  [key: string]: unknown;
}

function fmt(v: string): string {
  try {
    return new Decimal(v).toFixed(2);
  } catch {
    return v;
  }
}

const baseColumns: GridColumn<FinancialReportRow>[] = [
  {
    key: "nominalCode",
    header: "Code",
    sortable: true,
    sortAccessor: (r) => r.nominalCode,
    render: (r) => <span className="font-mono text-fg-muted">{r.nominalCode}</span>,
  },
  { key: "name", header: "Nominal", sortable: true, sortAccessor: (r) => r.name ?? "" },
  {
    key: "amount",
    header: "Amount",
    align: "right",
    sortable: true,
    sortAccessor: (r) => Number(r.amount),
    render: (r) => fmt(r.amount),
  },
];

interface FinancialReportBlockProps {
  title: string;
  rows: FinancialReportRow[];
  total: string;
  tone?: "ok" | "warn" | "neutral";
  showCategory?: boolean;
  drilldownDateFrom?: string;
  drilldownDateTo?: string;
}

export function FinancialReportBlock({
  title,
  rows,
  total,
  tone = "neutral",
  showCategory = false,
  drilldownDateFrom,
  drilldownDateTo,
}: FinancialReportBlockProps) {
  const toneClass =
    tone === "ok"
      ? "border-status-success/30 bg-status-success/10"
      : tone === "warn"
        ? "border-status-warning/30 bg-status-warning/10"
        : "border-border bg-surface";

  const columns = useMemo(
    () =>
      responsiveListColumns<FinancialReportRow>(
        showCategory
          ? [
              {
                ...baseColumns[0]!,
                render: (r) => (
                  <Link
                    href={buildGeneralLedgerHref({
                      nominalCode: r.nominalCode,
                      dateFrom: drilldownDateFrom,
                      dateTo: drilldownDateTo,
                    })}
                    className="font-mono text-brand hover:underline"
                  >
                    {r.nominalCode}
                  </Link>
                ),
              },
              baseColumns[1]!,
              {
                key: "categoryName",
                header: "Category",
                sortable: true,
                sortAccessor: (r) => r.categoryName ?? "",
              },
              baseColumns[2]!,
            ]
          : [
              {
                ...baseColumns[0]!,
                render: (r) => (
                  <Link
                    href={buildGeneralLedgerHref({
                      nominalCode: r.nominalCode,
                      dateFrom: drilldownDateFrom,
                      dateTo: drilldownDateTo,
                    })}
                    className="font-mono text-brand hover:underline"
                  >
                    {r.nominalCode}
                  </Link>
                ),
              },
              baseColumns[1]!,
              baseColumns[2]!,
            ],
        { primaryKey: "nominalCode" },
      ),
    [drilldownDateFrom, drilldownDateTo, showCategory],
  );

  return (
    <section className={cn("overflow-hidden rounded-lg border", toneClass)}>
      <div className="border-b border-current/10 px-4 py-2 text-sm font-semibold uppercase tracking-wide">
        {title}
      </div>
      <EnterpriseGrid<FinancialReportRow>
        columns={columns}
        rows={rows}
        emptyMessage="None."
        getRowId={(r) => r.nominalCode}
        skeletonRows={3}
      />
      <div className="flex items-center justify-between border-t-2 border-border bg-surface px-4 py-2 text-sm font-medium">
        <span className="text-right text-fg-muted">Total</span>
        <span className="tabular-nums">{fmt(total)}</span>
      </div>
    </section>
  );
}
