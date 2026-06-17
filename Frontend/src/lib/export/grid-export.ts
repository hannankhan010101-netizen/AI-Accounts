import type { GridColumn } from "@/components/ui/enterprise-grid";
import type { GridExportColumn } from "@/components/ui/grid-export-button";

type RowRecord = Record<string, unknown>;

/** Build CSV export config from grid column definitions. */
export function buildGridExport<Row extends RowRecord>(
  filename: string,
  columns: GridColumn<Row>[],
): { filename: string; columns: GridExportColumn<Row>[] } {
  return {
    filename,
    columns: columns.map((c) => ({
      header: c.header,
      value: (row) => {
        if (c.sortAccessor) {
          const v = c.sortAccessor(row);
          return v === null || v === undefined ? "" : String(v);
        }
        const raw = row[c.key];
        return raw === null || raw === undefined ? "" : String(raw);
      },
    })),
  };
}
