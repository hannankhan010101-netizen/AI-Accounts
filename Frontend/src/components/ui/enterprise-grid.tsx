"use client";

import {
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
  type ColumnDef,
  type Row,
  type SortingState,
} from "@tanstack/react-table";
import { useVirtualizer } from "@tanstack/react-virtual";
import { memo, useCallback, useEffect, useMemo, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import type { DataTablePagination } from "@/components/ui/data-table";
import {
  GridExportButton,
  type GridExportColumn,
} from "@/components/ui/grid-export-button";
import { ScrollHint } from "@/components/ui/scroll-hint";
import { useIsBelow, useIsMobile } from "@/lib/responsive";
import type { BreakpointKey } from "@/lib/responsive/constants";
import { registerGridTourScroll } from "@/lib/tour/grid-tour-bridge";
import { cn } from "@/lib/utils";
import { brandFocusedRowClasses } from "@/lib/design-tokens/brand-surfaces";
import { resolveListEmpty, type ListEntityKey } from "@/lib/list/list-empty-presets";
import Link from "next/link";

export interface GridColumn<Row> {
  key: string;
  header: string;
  /** Optional rich header (e.g. select-all checkbox). Falls back to `header` for export/a11y. */
  headerNode?: React.ReactNode;
  render?: (row: Row) => React.ReactNode;
  className?: string;
  align?: "left" | "right" | "center";
  sortable?: boolean;
  sortAccessor?: (row: Row) => string | number;
  /** Hide this column in table mode below the breakpoint */
  hideBelow?: BreakpointKey;
  /** Omit from mobile card layout (e.g. row checkboxes) */
  cardHidden?: boolean;
  /** Card layout label (defaults to header) */
  cardLabel?: string;
  /** Primary field on mobile cards */
  cardPrimary?: boolean;
}

type RowRecord = Record<string, unknown>;

export type GridLayout = "auto" | "table" | "cards";

interface EnterpriseGridProps<Row extends RowRecord> {
  columns: GridColumn<Row>[];
  rows: Row[] | undefined;
  loading?: boolean;
  fetching?: boolean;
  error?: unknown;
  emptyMessage?: string;
  /** Standardized empty state preset for list hubs */
  listEntity?: ListEntityKey;
  isSearching?: boolean;
  getRowId?: (row: Row, index: number) => string;
  rowClassName?: (row: Row) => string | undefined;
  skeletonRows?: number;
  pagination?: DataTablePagination;
  virtualizeThreshold?: number;
  onRowClick?: (row: Row) => void;
  exportCsv?: {
    filename: string;
    columns: GridExportColumn<Row>[];
    rows?: Row[];
  };
  tourTarget?: string;
  /** auto = cards below md; table = always table; cards = always cards */
  layout?: GridLayout;
}

function columnHidden<Row extends RowRecord>(
  col: GridColumn<Row>,
  belowSm: boolean,
  belowMd: boolean,
  belowLg: boolean,
): boolean {
  if (!col.hideBelow) return false;
  if (col.hideBelow === "sm" && belowSm) return true;
  if (col.hideBelow === "md" && belowMd) return true;
  if (col.hideBelow === "lg" && belowLg) return true;
  if (col.hideBelow === "xs" && belowSm) return true;
  return false;
}

function cellContent<Row extends RowRecord>(col: GridColumn<Row>, row: Row): React.ReactNode {
  return col.render ? col.render(row) : (row[col.key] as React.ReactNode) ?? "";
}

function toColumnDefs<Row extends RowRecord>(columns: GridColumn<Row>[]): ColumnDef<Row>[] {
  return columns.map((col) => ({
    id: col.key,
    accessorKey: col.render ? undefined : col.key,
    header: col.headerNode ?? col.header,
    enableSorting: col.sortable ?? Boolean(col.sortAccessor ?? !col.render),
    sortingFn: col.sortAccessor
      ? (a, b) => {
          const av = col.sortAccessor!(a.original as Row);
          const bv = col.sortAccessor!(b.original as Row);
          if (typeof av === "number" && typeof bv === "number") return av - bv;
          return String(av).localeCompare(String(bv));
        }
      : "alphanumeric",
    cell: ({ row }) => {
      const r = row.original as Row;
      if (r == null) return null;
      const content = cellContent(col, r);
      return (
        <div
          className={cn(
            col.align === "right" && "text-right tabular-nums",
            col.align === "center" && "text-center",
            col.className,
          )}
        >
          {content}
        </div>
      );
    },
    meta: { align: col.align, className: col.className },
  })) as ColumnDef<Row>[];
}

function TableSkeleton({ colCount, rowCount }: { colCount: number; rowCount: number }) {
  return (
    <>
      {Array.from({ length: rowCount }).map((_, ri) => (
        <tr key={ri} className="border-b border-border">
          {Array.from({ length: colCount }).map((__, ci) => (
            <td key={ci} className="px-3 py-2.5">
              <div
                className="h-4 animate-pulse rounded bg-canvas"
                style={{ width: ci === 0 ? "70%" : "45%" }}
              />
            </td>
          ))}
        </tr>
      ))}
    </>
  );
}

function CardSkeleton({ rowCount }: { rowCount: number }) {
  return (
    <ul className="divide-y divide-border" role="list" aria-busy="true">
      {Array.from({ length: rowCount }).map((_, i) => (
        <li key={i} className="p-4">
          <div className="mb-2 h-5 w-2/3 animate-pulse rounded bg-canvas" />
          <div className="space-y-2">
            <div className="h-3 w-full animate-pulse rounded bg-canvas" />
            <div className="h-3 w-4/5 animate-pulse rounded bg-canvas" />
          </div>
        </li>
      ))}
    </ul>
  );
}

const GridCard = memo(function GridCard<Row extends RowRecord>({
  row,
  rowIndex,
  columns,
  focused,
  onRowClick,
  rowClassName,
  tourTarget,
}: {
  row: Row;
  rowIndex: number;
  columns: GridColumn<Row>[];
  focused?: boolean;
  onRowClick?: (row: Row) => void;
  rowClassName?: (row: Row) => string | undefined;
  tourTarget?: string;
}) {
  const primary = columns.find((c) => c.cardPrimary) ?? columns[0];
  const secondary = columns.filter(
    (c) => c.key !== primary?.key && !c.cardHidden,
  );

  const rowTourId = tourTarget ? `${tourTarget}-row-${rowIndex}` : undefined;

  return (
    <li
      {...(rowTourId ? { "data-tour": rowTourId } : {})}
      className={cn(
        "border-b border-border-subtle/60 p-4 motion-safe-transition last:border-b-0 dark:divide-border-subtle/30",
        onRowClick && "cursor-pointer hover:bg-surface-elevated/60 active:bg-canvas",
        focused && brandFocusedRowClasses,
        rowClassName?.(row),
      )}
      onClick={
        onRowClick
          ? (e) => {
              const t = e.target as HTMLElement;
              if (t.closest("input,button,a,select,textarea")) return;
              onRowClick(row);
            }
          : undefined
      }
    >
      {primary && (
        <div className="mb-2 font-medium text-fg">{cellContent(primary, row)}</div>
      )}
      {secondary.length > 0 && (
        <dl className="grid grid-cols-[minmax(5rem,auto)_1fr] gap-x-3 gap-y-1.5 text-sm">
          {secondary.map((col) => (
            <div key={col.key} className="contents">
              <dt className="text-fg-muted">{col.cardLabel ?? col.header}</dt>
              <dd
                className={cn(
                  "min-w-0 text-fg",
                  col.align === "right" && "text-right tabular-nums",
                )}
              >
                {cellContent(col, row)}
              </dd>
            </div>
          ))}
        </dl>
      )}
    </li>
  );
}) as <Row extends RowRecord>(props: {
  row: Row;
  rowIndex: number;
  columns: GridColumn<Row>[];
  focused?: boolean;
  onRowClick?: (row: Row) => void;
  rowClassName?: (row: Row) => string | undefined;
  tourTarget?: string;
}) => React.ReactElement | null;

function GridPagination({
  pagination,
  pageCount,
  loading,
}: {
  pagination: DataTablePagination;
  pageCount: number;
  loading?: boolean;
}) {
  const isMobile = useIsMobile();
  return (
    <div className="flex flex-wrap items-center justify-between gap-2 text-sm text-fg-muted">
      <span>
        {(pagination.page - 1) * pagination.pageSize + 1}–
        {Math.min(pagination.page * pagination.pageSize, pagination.totalItems)} of{" "}
        {pagination.totalItems}
      </span>
      <div className={cn("flex items-center gap-2", isMobile && "w-full justify-between")}>
        <Button
          variant="outline"
          size={isMobile ? "lg" : "sm"}
          className={isMobile ? "flex-1 touch-target" : undefined}
          disabled={pagination.page <= 1 || loading}
          onClick={() => pagination.onPageChange(pagination.page - 1)}
        >
          Previous
        </Button>
        <span className="tabular-nums">
          Page {pagination.page} / {pageCount}
        </span>
        <Button
          variant="outline"
          size={isMobile ? "lg" : "sm"}
          className={isMobile ? "flex-1 touch-target" : undefined}
          disabled={pagination.page >= pageCount || loading}
          onClick={() => pagination.onPageChange(pagination.page + 1)}
        >
          Next
        </Button>
      </div>
    </div>
  );
}

export function EnterpriseGrid<Row extends RowRecord>({
  columns,
  rows,
  loading,
  fetching,
  error,
  emptyMessage = "No records found.",
  listEntity,
  isSearching = false,
  getRowId,
  rowClassName,
  skeletonRows = 8,
  pagination,
  virtualizeThreshold = 80,
  onRowClick,
  exportCsv,
  tourTarget,
  layout = "auto",
}: EnterpriseGridProps<Row>) {
  const isMobile = useIsMobile();
  const belowSm = useIsBelow("sm");
  const belowMd = useIsBelow("md");
  const belowLg = useIsBelow("lg");
  const showCards =
    layout === "cards" || (layout === "auto" && isMobile);

  const visibleColumns = useMemo(
    () =>
      showCards
        ? columns
        : columns.filter((c) => !columnHidden(c, belowSm, belowMd, belowLg)),
    [columns, showCards, belowSm, belowMd, belowLg],
  );

  const [sorting, setSorting] = useState<SortingState>([]);
  const [focusedRowIndex, setFocusedRowIndex] = useState(-1);
  const parentRef = useRef<HTMLDivElement>(null);

  const data = useMemo(
    () => (rows ?? []).filter((row): row is Row => row != null),
    [rows],
  );
  const columnDefs = useMemo(() => toColumnDefs(visibleColumns), [visibleColumns]);

  const defaultRowId = useCallback((original: Row, index: number) => {
    const id = original?.id;
    return id != null && id !== "" ? String(id) : `row-${index}`;
  }, []);

  const table = useReactTable({
    data,
    columns: columnDefs,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getRowId: getRowId ?? defaultRowId,
  });

  const tableRows = table.getRowModel().rows;
  const useVirtual = !showCards && !loading && tableRows.length > virtualizeThreshold;

  useEffect(() => {
    setFocusedRowIndex((i) => {
      if (tableRows.length === 0) return -1;
      if (i < 0) return i;
      return Math.min(i, tableRows.length - 1);
    });
  }, [tableRows.length, sorting]);

  const onGridKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLDivElement>) => {
      if (loading || tableRows.length === 0) return;
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setFocusedRowIndex((i) =>
          i < 0 ? 0 : Math.min(i + 1, tableRows.length - 1),
        );
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setFocusedRowIndex((i) => (i <= 0 ? -1 : i - 1));
      } else if (e.key === "Enter" && onRowClick) {
        if (focusedRowIndex < 0) return;
        const row = tableRows[focusedRowIndex];
        if (row) {
          e.preventDefault();
          onRowClick(row.original as Row);
        }
      } else if (e.key === "Home") {
        e.preventDefault();
        setFocusedRowIndex(0);
      } else if (e.key === "End") {
        e.preventDefault();
        setFocusedRowIndex(tableRows.length - 1);
      }
    },
    [loading, tableRows, focusedRowIndex, onRowClick],
  );

  const virtualizer = useVirtualizer({
    count: tableRows.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 40,
    overscan: 12,
    enabled: useVirtual,
  });

  useEffect(() => {
    if (!tourTarget) return;
    return registerGridTourScroll(tourTarget, (rowIndex) => {
      const idx = Math.min(Math.max(0, rowIndex), Math.max(0, tableRows.length - 1));
      setFocusedRowIndex(idx);
      if (useVirtual) {
        virtualizer.scrollToIndex(idx, { align: "center" });
      }
      requestAnimationFrame(() => {
        const rowEl = parentRef.current?.querySelector<HTMLElement>(
          `[data-tour="${tourTarget}-row-${idx}"]`,
        );
        rowEl?.scrollIntoView({ block: "nearest", inline: "nearest", behavior: "smooth" });
      });
    });
  }, [tourTarget, useVirtual, tableRows.length, virtualizer]);

  if (error instanceof Error) {
    return (
      <div className="rounded-md border border-status-danger/30 bg-status-danger/10 p-3 text-sm text-status-danger" role="alert">
        {error.message}
      </div>
    );
  }

  const pageCount = pagination
    ? Math.max(1, Math.ceil(pagination.totalItems / pagination.pageSize))
    : 0;

  const emptyState = listEntity ? (
    (() => {
      const preset = resolveListEmpty(listEntity, isSearching);
      return (
        <EmptyState
          icon={preset.icon}
          title={preset.title}
          description={preset.description}
          className="py-8"
          action={
            !isSearching && preset.createHref ? (
              <Button asChild size="sm">
                <Link href={preset.createHref}>{preset.createLabel ?? "Create"}</Link>
              </Button>
            ) : undefined
          }
        />
      );
    })()
  ) : (
    <EmptyState description={emptyMessage} className="py-8" />
  );

  const virtualRows = useVirtual ? virtualizer.getVirtualItems() : null;
  const totalHeight = useVirtual ? virtualizer.getTotalSize() : 0;
  const paddingTop = virtualRows?.[0]?.start ?? 0;
  const paddingBottom = useVirtual
    ? totalHeight - (virtualRows?.[virtualRows.length - 1]?.end ?? 0)
    : 0;

  return (
    <div className="space-y-2">
      <div className="relative">
        {fetching && !loading && (
          <div
            className="absolute inset-x-0 top-0 z-20 h-0.5 overflow-hidden rounded-t-lg bg-canvas"
            aria-hidden
          >
            <div className="h-full w-1/3 animate-pulse bg-brand-600 motion-reduce:animate-none" />
          </div>
        )}

        {showCards ? (
          <div
            ref={parentRef}
            role="region"
            tabIndex={0}
            aria-busy={fetching || loading}
            aria-label="Data list. Use arrow keys to move between rows, Enter to open a row."
            onKeyDown={onGridKeyDown}
            {...(tourTarget ? { "data-tour": tourTarget } : {})}
            className={cn(
              "overflow-y-auto rounded-xl bg-surface shadow-sm dark:border-0 dark:bg-surface-elevated/90 dark:shadow-md",
            )}
          >
            {exportCsv ? (
              <div className="flex justify-end border-b border-border-subtle/60 px-3 py-1.5 no-print dark:border-border-subtle/30">
                <GridExportButton
                  filename={exportCsv.filename}
                  rows={exportCsv.rows ?? rows}
                  columns={exportCsv.columns}
                  disabled={loading}
                />
              </div>
            ) : null}
            {loading && <CardSkeleton rowCount={skeletonRows} />}
            {!loading && tableRows.length === 0 && emptyState}
            {!loading && tableRows.length > 0 && (
              <ul role="list" className="divide-y divide-border-subtle/60 dark:divide-border-subtle/30">
                {tableRows.map((row, index) => (
                  <GridCard
                    key={row.id}
                    row={row.original as Row}
                    rowIndex={index}
                    columns={columns}
                    focused={focusedRowIndex >= 0 && index === focusedRowIndex}
                    onRowClick={onRowClick}
                    rowClassName={rowClassName}
                    tourTarget={tourTarget}
                  />
                ))}
              </ul>
            )}
          </div>
        ) : (
          <div
            ref={parentRef}
            tabIndex={0}
            role="region"
            aria-busy={fetching || loading}
            aria-label="Data table. Use arrow keys to move between rows, Enter to open a row."
            onKeyDown={onGridKeyDown}
            {...(tourTarget ? { "data-tour": tourTarget } : {})}
            className={cn(
              "scrollbar-gutter-stable overflow-x-auto overflow-y-auto rounded-xl bg-surface shadow-sm motion-safe-transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--focus-ring)] dark:border-0 dark:bg-surface-elevated/90 dark:shadow-md",
              useVirtual && "max-h-[min(70vh,640px)] max-h-sm:max-h-[min(50vh,400px)]",
            )}
          >
            {exportCsv ? (
              <div className="flex justify-end border-b border-border-subtle/60 px-3 py-1.5 no-print dark:border-border-subtle/30">
                <GridExportButton
                  filename={exportCsv.filename}
                  rows={exportCsv.rows ?? rows}
                  columns={exportCsv.columns}
                  disabled={loading}
                />
              </div>
            ) : null}
            {isMobile && visibleColumns.length > 3 && <ScrollHint />}
            <table className="min-w-full text-sm">
              <thead
                className={cn(
                  "bg-surface-elevated/95 dark:bg-surface-elevated/90",
                  useVirtual && "sticky top-0 z-10 backdrop-blur-sm",
                )}
              >
                {table.getHeaderGroups().map((hg) => (
                  <tr
                    key={hg.id}
                    className="border-b border-border-subtle/80 text-left text-xs uppercase tracking-wide text-fg-muted dark:border-border-subtle/40"
                  >
                    {hg.headers.map((header) => {
                      const align = (header.column.columnDef.meta as { align?: string })?.align;
                      const canSort = header.column.getCanSort();
                      return (
                        <th
                          key={header.id}
                          scope="col"
                          className={cn(
                            "px-3 py-2",
                            align === "right" && "text-right",
                            align === "center" && "text-center",
                            header.column.getIsSorted() && "text-brand",
                          )}
                          aria-sort={
                            canSort
                              ? header.column.getIsSorted() === "asc"
                                ? "ascending"
                                : header.column.getIsSorted() === "desc"
                                  ? "descending"
                                  : "none"
                              : undefined
                          }
                        >
                          {canSort ? (
                            <button
                              type="button"
                              className="inline-flex w-full items-center gap-1 text-left hover:text-brand focus-ring"
                              onClick={header.column.getToggleSortingHandler()}
                            >
                              {flexRender(header.column.columnDef.header, header.getContext())}
                              <span className="text-[10px] text-fg-muted" aria-hidden>
                                {header.column.getIsSorted() === "asc"
                                  ? "↑"
                                  : header.column.getIsSorted() === "desc"
                                    ? "↓"
                                    : "↕"}
                              </span>
                            </button>
                          ) : (
                            flexRender(header.column.columnDef.header, header.getContext())
                          )}
                        </th>
                      );
                    })}
                  </tr>
                ))}
              </thead>
              <tbody>
                {loading && (
                  <TableSkeleton colCount={visibleColumns.length} rowCount={skeletonRows} />
                )}
                {!loading && tableRows.length === 0 && (
                  <tr>
                    <td
                      colSpan={visibleColumns.length}
                      className="p-0"
                    >
                      {emptyState}
                    </td>
                  </tr>
                )}
                {!loading &&
                  !useVirtual &&
                  tableRows.map((row, index) => (
                    <GridRow
                      key={row.id}
                      row={row}
                      rowIndex={index}
                      focused={focusedRowIndex >= 0 && index === focusedRowIndex}
                      onRowClick={onRowClick}
                      rowClassName={rowClassName}
                      tourTarget={tourTarget}
                    />
                  ))}
                {!loading && useVirtual && (
                  <>
                    {paddingTop > 0 && (
                      <tr>
                        <td colSpan={visibleColumns.length} style={{ height: paddingTop }} />
                      </tr>
                    )}
                    {virtualRows?.map((vRow) => {
                      const row = tableRows[vRow.index];
                      if (!row) return null;
                      return (
                        <GridRow
                          key={row.id}
                          row={row}
                          rowIndex={vRow.index}
                          focused={focusedRowIndex >= 0 && vRow.index === focusedRowIndex}
                          onRowClick={onRowClick}
                          rowClassName={rowClassName}
                          tourTarget={tourTarget}
                        />
                      );
                    })}
                    {paddingBottom > 0 && (
                      <tr>
                        <td colSpan={visibleColumns.length} style={{ height: paddingBottom }} />
                      </tr>
                    )}
                  </>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {pagination && !loading && pagination.totalItems > 0 && (
        <GridPagination pagination={pagination} pageCount={pageCount} loading={loading} />
      )}
    </div>
  );
}

function GridRow<TRow extends RowRecord>({
  row,
  rowIndex,
  focused,
  onRowClick,
  rowClassName,
  tourTarget,
}: {
  row: Row<TRow>;
  rowIndex: number;
  focused?: boolean;
  onRowClick?: (row: TRow) => void;
  rowClassName?: (row: TRow) => string | undefined;
  tourTarget?: string;
}) {
  const original = row.original as TRow;
  if (original == null) return null;

  const rowTourId = tourTarget ? `${tourTarget}-row-${rowIndex}` : undefined;
  return (
    <tr
      aria-rowindex={rowIndex + 1}
      {...(rowTourId ? { "data-tour": rowTourId } : {})}
      className={cn(
        "border-b border-border-subtle/80 last:border-b-0 motion-safe-transition hover:bg-surface-muted/60 dark:border-border-subtle/30 dark:hover:bg-surface-muted/40",
        onRowClick && "cursor-pointer",
        focused && brandFocusedRowClasses,
        rowClassName?.(original),
      )}
      onClick={
        onRowClick
          ? (e) => {
              const t = e.target as HTMLElement;
              if (t.closest("input,button,a,select,textarea")) return;
              onRowClick(original);
            }
          : undefined
      }
    >
      {row.getVisibleCells().map((cell) => {
        const align = (cell.column.columnDef.meta as { align?: string })?.align;
        return (
          <td
            key={cell.id}
            className={cn(
              "px-3 py-2 align-top",
              align === "right" && "text-right",
              align === "center" && "text-center",
            )}
          >
            {flexRender(cell.column.columnDef.cell, cell.getContext())}
          </td>
        );
      })}
    </tr>
  );
}
