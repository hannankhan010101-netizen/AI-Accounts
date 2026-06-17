import { recordsToCsv, tableToCsv } from "@/lib/export/csv";
import type { FinancialReportRow } from "@/components/reports/financial-report-block";

export function financialSectionsToCsv(
  sections: { section: string; rows: FinancialReportRow[] }[],
): string {
  const flat = sections.flatMap(({ section, rows }) =>
    rows.map((r) => ({
      section,
      nominalCode: r.nominalCode,
      name: r.name ?? "",
      categoryName: r.categoryName ?? "",
      amount: r.amount,
    })),
  );
  return recordsToCsv(flat, ["section", "nominalCode", "name", "categoryName", "amount"]);
}

export function dynamicRowsToCsv(rows: Record<string, unknown>[]): string {
  return recordsToCsv(rows);
}

export { tableToCsv, recordsToCsv };
