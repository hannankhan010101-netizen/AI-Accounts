/** Client-side CSV download helpers for reports and grid exports. */

function escapeCell(value: unknown): string {
  if (value === null || value === undefined) return "";
  const s = String(value);
  if (/[",\n\r]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
  return s;
}

export function recordsToCsv(
  rows: Record<string, unknown>[],
  columnOrder?: string[],
): string {
  if (rows.length === 0) return "";
  const keys =
    columnOrder ??
    Array.from(
      rows.reduce((set, row) => {
        Object.keys(row).forEach((k) => set.add(k));
        return set;
      }, new Set<string>()),
    );
  const header = keys.map(escapeCell).join(",");
  const body = rows
    .map((row) => keys.map((k) => escapeCell(row[k])).join(","))
    .join("\n");
  return `${header}\n${body}`;
}

export function tableToCsv(headers: string[], rows: string[][]): string {
  const lines = [
    headers.map(escapeCell).join(","),
    ...rows.map((r) => r.map(escapeCell).join(",")),
  ];
  return lines.join("\n");
}

export function downloadCsv(filename: string, csvText: string): void {
  const blob = new Blob([csvText], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename.endsWith(".csv") ? filename : `${filename}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

export function downloadRecordsCsv(
  filename: string,
  rows: Record<string, unknown>[],
  columnOrder?: string[],
): void {
  downloadCsv(filename, recordsToCsv(rows, columnOrder));
}
