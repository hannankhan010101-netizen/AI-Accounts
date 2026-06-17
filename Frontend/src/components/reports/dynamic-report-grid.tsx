"use client";

import Link from "next/link";
import { useMemo } from "react";

import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { ListToolbar } from "@/components/ui/list-toolbar";
import { useClientList } from "@/lib/hooks/use-client-list";
import { matchText } from "@/lib/list/document-list-filters";
import { buildDynamicReportCellHref, type ReportDrillContext } from "@/lib/reports/report-drilldown";

export type DynamicReportRow = Record<string, unknown>;

function cellValue(v: unknown): string {
  if (v == null) return "";
  if (typeof v === "object") return JSON.stringify(v);
  return String(v);
}

function titleizeKey(key: string): string {
  return key
    .replace(/([A-Z])/g, " $1")
    .replace(/_/g, " ")
    .replace(/^\w/, (c) => c.toUpperCase())
    .trim();
}

interface DynamicReportGridProps {
  rows: DynamicReportRow[];
  loading?: boolean;
  error?: unknown;
  emptyMessage?: string;
  drillContext?: ReportDrillContext;
}

export function DynamicReportGrid({
  rows,
  loading,
  error,
  emptyMessage = "No rows for this period.",
  drillContext,
}: DynamicReportGridProps) {
  const columnKeys = useMemo(
    () => (rows.length > 0 ? Object.keys(rows[0]) : []),
    [rows],
  );

  const { search, setSearch, pageRows, pagination } = useClientList({
    rows,
    filterFn: (r, q) => matchText(columnKeys.map((k) => cellValue(r[k])), q),
  });

  const columns = useMemo(
    () =>
      responsiveListColumns<DynamicReportRow>(
        columnKeys.map((key) => ({
        key,
        header: titleizeKey(key),
        sortable: true,
        sortAccessor: (r) => cellValue(r[key]),
        render: (r) => {
          const v = r[key];
          const href = buildDynamicReportCellHref(key, v, r, drillContext);
          const isNum =
            typeof v === "number" ||
            (typeof v === "string" && v !== "" && !Number.isNaN(Number(v)));
          const text = cellValue(v);
          if (href && text) {
            return (
              <Link href={href} className="text-brand hover:underline tabular-nums">
                {text}
              </Link>
            );
          }
          return (
            <span className={isNum ? "tabular-nums" : undefined}>{text}</span>
          );
        },
        align:
          typeof rows[0]?.[key] === "number" ||
          (typeof rows[0]?.[key] === "string" &&
            rows[0]?.[key] !== "" &&
            !Number.isNaN(Number(rows[0]?.[key])))
            ? "right"
            : "left",
        })),
      ),
    [columnKeys, rows, drillContext],
  );

  return (
    <>
      {columnKeys.length > 0 && (
        <ListToolbar search={search} onSearchChange={setSearch} className="mb-3" />
      )}
      <EnterpriseGrid<DynamicReportRow>
        columns={columns}
        rows={pageRows}
        loading={loading}
        error={error}
        emptyMessage={emptyMessage}
        getRowId={(_, i) => String(i)}
        pagination={pagination}
      />
    </>
  );
}
