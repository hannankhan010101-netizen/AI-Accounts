import { readFile } from "node:fs/promises";
import type { EntityModule } from "../types/pipeline.js";
import type { StreamRow } from "./csv-stream.js";

const MODULE_KEY_MAP: Record<string, EntityModule> = {
  sales_customers: "customers",
  sales_invoices: "invoices",
  sales_receipts: "receipts",
  purchase_suppliers: "suppliers",
  purchase_bills: "bills",
  purchase_payments: "payments",
  inventory_products: "products",
  settings_coa: "chart_of_accounts",
  settings_taxes: "taxes",
  settings_journals: "journals",
  bank_payments: "bank_transactions",
};

interface LabeledExport {
  sections: Array<{
    moduleKey: string;
    moduleLabel: string;
    category: string;
    records: Record<string, unknown>[];
  }>;
}

export async function* streamFastAccountsLabeled(
  filePath: string,
  moduleFilter?: EntityModule,
): AsyncGenerator<StreamRow & { module: EntityModule; sectionKey: string }> {
  const raw = await readFile(filePath, "utf-8");
  const data = JSON.parse(raw) as LabeledExport;

  for (const section of data.sections) {
    const module = MODULE_KEY_MAP[section.moduleKey];
    if (!module) continue;
    if (moduleFilter && module !== moduleFilter) continue;

    let rowIndex = 0;
    for (const record of section.records) {
      rowIndex++;
      yield {
        rowIndex,
        data: record,
        module,
        sectionKey: section.moduleKey,
      };
    }
  }
}

export function listFastAccountsSections(filePath: string): Promise<
  Array<{ moduleKey: string; module: EntityModule | null; recordCount: number }>
> {
  return readFile(filePath, "utf-8").then((raw) => {
    const data = JSON.parse(raw) as LabeledExport;
    return data.sections.map((s) => ({
      moduleKey: s.moduleKey,
      module: MODULE_KEY_MAP[s.moduleKey] ?? null,
      recordCount: s.records.length,
    }));
  });
}
