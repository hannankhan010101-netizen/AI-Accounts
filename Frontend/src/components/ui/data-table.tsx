"use client";

import { type ReactNode } from "react";

import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { cn } from "@/lib/utils";

export interface Column<Row> {
  key: string;
  header: string;
  render?: (row: Row) => ReactNode;
  className?: string;
  align?: "left" | "right" | "center";
}

export interface DataTablePagination {
  page: number;
  pageSize: number;
  totalItems: number;
  onPageChange: (page: number) => void;
}

interface DataTableProps<Row> {
  columns: Column<Row>[];
  rows: Row[] | undefined;
  loading?: boolean;
  error?: unknown;
  emptyMessage?: string;
  getRowId?: (row: Row, index: number) => string;
  rowClassName?: (row: Row) => string | undefined;
  /** Skeleton row count while loading (default 5) */
  skeletonRows?: number;
  pagination?: DataTablePagination;
}

function TableSkeleton({ columns, rows }: { columns: number; rows: number }) {
  return (
    <>
      {Array.from({ length: rows }).map((_, ri) => (
        <tr key={ri} className="border-b border-border">
          {Array.from({ length: columns }).map((__, ci) => (
            <td key={ci} className="px-3 py-2.5">
              <div
                className="h-4 animate-pulse rounded bg-surface-muted"
                style={{ width: ci === 0 ? "70%" : ci % 2 === 0 ? "55%" : "40%" }}
              />
            </td>
          ))}
        </tr>
      ))}
    </>
  );
}

type RowRecord = Record<string, unknown>;

export function DataTable<Row extends RowRecord>({
  columns,
  rows,
  loading,
  error,
  emptyMessage = "No records found.",
  getRowId,
  rowClassName,
  skeletonRows = 5,
  pagination,
}: DataTableProps<Row>) {
  if (error instanceof Error) {
    return (
      <div
        className="rounded-md border border-status-danger/30 bg-status-danger/10 p-3 text-sm text-status-danger"
        role="alert"
      >
        {error.message}
      </div>
    );
  }

  const pageCount = pagination
    ? Math.max(1, Math.ceil(pagination.totalItems / pagination.pageSize))
    : 0;

  return (
    <div className="space-y-2">
      <div className="overflow-x-auto rounded-lg border border-border bg-surface shadow-sm dark:border-0 dark:bg-surface-elevated/90 dark:shadow-md">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="border-b border-border bg-surface-elevated text-left text-xs uppercase tracking-wide text-fg-muted dark:bg-surface-elevated/90">
              {columns.map((col) => (
                <th
                  key={col.key}
                  scope="col"
                  className={cn(
                    "px-3 py-2",
                    col.align === "right" && "text-right",
                    col.align === "center" && "text-center",
                    col.className,
                  )}
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading && (
              <TableSkeleton columns={columns.length} rows={skeletonRows} />
            )}
            {!loading && rows && rows.length === 0 && (
              <tr>
                <td colSpan={columns.length} className="p-0">
                  <EmptyState description={emptyMessage} />
                </td>
              </tr>
            )}
            {!loading &&
              rows?.map((row, i) => (
                <tr
                  key={getRowId ? getRowId(row, i) : (row.id as string) ?? String(i)}
                  className={cn(
                    "border-b border-border last:border-b-0 motion-safe-transition hover:bg-canvas/60",
                    rowClassName?.(row),
                  )}
                >
                  {columns.map((col) => (
                    <td
                      key={col.key}
                      className={cn(
                        "px-3 py-2 align-top",
                        col.align === "right" && "text-right tabular-nums",
                        col.align === "center" && "text-center",
                        col.className,
                      )}
                    >
                      {col.render ? col.render(row) : (row[col.key] as ReactNode) ?? ""}
                    </td>
                  ))}
                </tr>
              ))}
          </tbody>
        </table>
      </div>

      {pagination && !loading && pagination.totalItems > 0 && (
        <div className="flex flex-wrap items-center justify-between gap-2 text-sm text-fg-muted">
          <span>
            {(pagination.page - 1) * pagination.pageSize + 1}–
            {Math.min(pagination.page * pagination.pageSize, pagination.totalItems)} of{" "}
            {pagination.totalItems}
          </span>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={pagination.page <= 1}
              onClick={() => pagination.onPageChange(pagination.page - 1)}
            >
              Previous
            </Button>
            <span className="tabular-nums">
              Page {pagination.page} / {pageCount}
            </span>
            <Button
              variant="outline"
              size="sm"
              disabled={pagination.page >= pageCount}
              onClick={() => pagination.onPageChange(pagination.page + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
