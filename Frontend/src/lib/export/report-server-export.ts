import { downloadCsv } from "@/lib/export/csv";

export interface ReportServerExportResult {
  format: string;
  content?: string | null;
}

/** Download inline export payload from POST /reports/export or /reports/runs/{id}/export. */
export function downloadReportServerExport(
  filenameBase: string,
  result: ReportServerExportResult,
): void {
  const fmt = (result.format || "csv").toLowerCase();
  const content = result.content ?? "";
  if (!content.trim()) return;

  if (fmt === "pdf") {
    const binary = atob(content);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i += 1) {
      bytes[i] = binary.charCodeAt(i);
    }
    const blob = new Blob([bytes], { type: "application/pdf" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${filenameBase}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
    return;
  }

  if (fmt === "json") {
    const blob = new Blob([content], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${filenameBase}.json`;
    a.click();
    URL.revokeObjectURL(url);
    return;
  }

  downloadCsv(filenameBase, content);
}
