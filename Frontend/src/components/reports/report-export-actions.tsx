"use client";

import { Button } from "@/components/ui/button";
import { downloadCsv } from "@/lib/export/csv";

interface ReportExportActionsProps {
  /** Base filename without extension. */
  filename: string;
  /** When false, buttons are disabled (no data yet). */
  enabled?: boolean;
  /** Build CSV text from current report data. */
  buildCsv?: () => string;
  /** Server-side PDF export (POST /reports/export). */
  onExportPdf?: () => void | Promise<void>;
  /** Server-side export in progress. */
  exportingPdf?: boolean;
  /** Element id to print (defaults to `report-print-area`). */
  printTargetId?: string;
  className?: string;
}

export function ReportExportActions({
  filename,
  enabled = true,
  buildCsv,
  onExportPdf,
  exportingPdf = false,
  printTargetId = "report-print-area",
  className,
}: ReportExportActionsProps) {
  const onPrint = () => {
    const el = document.getElementById(printTargetId);
    if (!el) {
      window.print();
      return;
    }
    window.print();
  };

  const onExport = () => {
    if (!buildCsv) return;
    const csv = buildCsv();
    if (!csv.trim()) return;
    downloadCsv(filename, csv);
  };

  return (
    <div className={className ?? "flex flex-wrap gap-2"}>
      <Button type="button" variant="outline" disabled={!enabled} onClick={onPrint}>
        Print
      </Button>
      {buildCsv ? (
        <Button type="button" variant="outline" disabled={!enabled} onClick={onExport}>
          Export CSV
        </Button>
      ) : null}
      {onExportPdf ? (
        <Button
          type="button"
          variant="outline"
          disabled={!enabled || exportingPdf}
          onClick={() => void onExportPdf()}
        >
          {exportingPdf ? "Exporting PDF…" : "Export PDF"}
        </Button>
      ) : null}
    </div>
  );
}
