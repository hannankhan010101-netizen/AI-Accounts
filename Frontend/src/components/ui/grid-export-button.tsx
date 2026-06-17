"use client";

import { Button } from "@/components/ui/button";
import { tableToCsv, downloadCsv } from "@/lib/export/csv";

export interface GridExportColumn<Row> {
  header: string;
  value: (row: Row) => string | number | null | undefined;
}

interface GridExportButtonProps<Row> {
  filename: string;
  rows: Row[] | undefined;
  columns: GridExportColumn<Row>[];
  disabled?: boolean;
}

/** Export visible grid rows to CSV (uses raw values, not React render output). */
export function GridExportButton<Row>({
  filename,
  rows,
  columns,
  disabled,
}: GridExportButtonProps<Row>) {
  const onExport = () => {
    if (!rows?.length) return;
    const headers = columns.map((c) => c.header);
    const data = rows.map((row) =>
      columns.map((c) => {
        const v = c.value(row);
        return v === null || v === undefined ? "" : String(v);
      }),
    );
    downloadCsv(filename, tableToCsv(headers, data));
  };

  return (
    <Button
      type="button"
      variant="outline"
      size="sm"
      disabled={disabled || !rows?.length}
      onClick={onExport}
    >
      Export CSV
    </Button>
  );
}
