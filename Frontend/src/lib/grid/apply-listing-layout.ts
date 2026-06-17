import type { GridColumn } from "@/components/ui/enterprise-grid";
import type { ListingColumnSetting } from "@/lib/api/tenant";

/** Apply Content Settings column layout to a grid definition. */
export function applyListingLayout<Row extends Record<string, unknown>>(
  columns: GridColumn<Row>[],
  layout: ListingColumnSetting[] | undefined,
): GridColumn<Row>[] {
  if (!layout?.length) return columns;

  const byKey = new Map(layout.map((c) => [c.key, c]));
  const orderedKeys = [...layout]
    .filter((c) => c.active)
    .sort((a, b) => a.order - b.order)
    .map((c) => c.key);

  const columnByKey = new Map(columns.map((c) => [c.key, c]));
  const out: GridColumn<Row>[] = [];

  for (const key of orderedKeys) {
    const col = columnByKey.get(key);
    const cfg = byKey.get(key);
    if (!col || !cfg) continue;
    out.push({
      ...col,
      header: cfg.label || col.header,
      cardLabel: cfg.label || col.cardLabel,
    });
  }

  for (const col of columns) {
    const cfg = byKey.get(col.key);
    if (cfg && !cfg.active) continue;
    if (out.some((c) => c.key === col.key)) continue;
    out.push(col);
  }

  return out.length ? out : columns;
}
