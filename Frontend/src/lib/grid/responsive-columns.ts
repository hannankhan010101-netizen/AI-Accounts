import type { GridColumn } from "@/components/ui/enterprise-grid";

/**
 * Applies mobile card + tablet table column defaults for standard list grids.
 * First column = cardPrimary; middle columns hidden in table below md.
 */
export function responsiveListColumns<Row extends Record<string, unknown>>(
  columns: GridColumn<Row>[],
  options?: {
    primaryKey?: string;
    /** Column keys to hide in compact table mode (defaults: all except first and last) */
    hideBelowMdKeys?: string[];
  },
): GridColumn<Row>[] {
  if (columns.length === 0) return columns;

  const primaryKey = options?.primaryKey ?? columns[0]?.key;
  const lastKey = columns[columns.length - 1]?.key;
  const defaultHide = columns
    .map((c) => c.key)
    .filter((k) => k !== primaryKey && k !== lastKey);
  const hideSet = new Set(options?.hideBelowMdKeys ?? defaultHide);

  return columns.map((col) => ({
    ...col,
    cardPrimary: col.cardPrimary ?? col.key === primaryKey,
    hideBelow: col.hideBelow ?? (hideSet.has(col.key) ? "md" : undefined),
    cardLabel: col.cardLabel ?? col.header,
  }));
}
