import { createHash } from "node:crypto";
import { Decimal } from "decimal.js";
import type { EntityModule, StagingRecord } from "../types/pipeline.js";
import { parseDate } from "./validation-engine.js";

export function rowFingerprint(
  module: EntityModule,
  data: Record<string, unknown>,
): string {
  const keys = fingerprintKeysForModule(module);
  const parts = keys.map((k) => `${k}=${normalizeFingerprintValue(data[k])}`);
  return createHash("sha256").update(parts.join("|")).digest("hex");
}

function fingerprintKeysForModule(module: EntityModule): string[] {
  const map: Record<EntityModule, string[]> = {
    customers: ["code"],
    suppliers: ["code"],
    products: ["code"],
    projects: ["code"],
    chart_of_accounts: ["code"],
    taxes: ["code"],
    invoices: ["invoiceNumber"],
    bills: ["billNumber"],
    receipts: ["receiptNumber"],
    payments: ["voucherNumber"],
    bank_transactions: ["voucherNumber", "transactionDate"],
    stock_movements: ["reference", "productCode"],
    journals: ["journalNumber"],
  };
  return map[module] ?? ["code"];
}

function normalizeFingerprintValue(value: unknown): string {
  if (value === undefined || value === null) return "";
  return String(value).trim().toLowerCase();
}

export interface DedupeResult {
  records: StagingRecord[];
  duplicateCount: number;
}

/** Mark duplicates within chunk; optional existing fingerprints from prior runs. */
export function dedupeRecords(
  module: EntityModule,
  records: StagingRecord[],
  existingFingerprints: Set<string> = new Set(),
): DedupeResult {
  const seen = new Set<string>(existingFingerprints);
  let duplicateCount = 0;

  const updated = records.map((record) => {
    const data = record.transformedData ?? record.mappedData ?? record.sourceData;
    const fp = rowFingerprint(module, data);
    const isDuplicate = seen.has(fp);
    if (!isDuplicate) seen.add(fp);

    if (isDuplicate) duplicateCount++;

    return {
      ...record,
      fingerprint: fp,
      isDuplicate,
      externalId: externalIdFromData(module, data),
    };
  });

  return { records: updated, duplicateCount };
}

function externalIdFromData(
  module: EntityModule,
  data: Record<string, unknown>,
): string | undefined {
  const idField = fingerprintKeysForModule(module)[0];
  const val = data[idField] ?? data.ID ?? data.id ?? data["Invoice No"];
  return val !== undefined ? String(val) : undefined;
}

export function transformRow(
  module: EntityModule,
  data: Record<string, unknown>,
  options: { timezone?: string; baseCurrency?: string } = {},
): Record<string, unknown> {
  const out: Record<string, unknown> = { ...data };

  for (const [key, value] of Object.entries(out)) {
    if (typeof value === "string") {
      out[key] = value.trim();
    }
  }

  const dateFields = dateFieldsForModule(module);
  for (const field of dateFields) {
    if (out[field]) {
      const parsed = parseDate(String(out[field]));
      if (parsed) out[field] = parsed.toISOString();
    }
  }

  const decimalFields = decimalFieldsForModule(module);
  for (const field of decimalFields) {
    if (out[field] !== undefined) {
      out[field] = normalizeDecimal(out[field]);
    }
  }

  out._meta = {
    module,
    entityType: module,
    side: sideForModule(module),
    timezone: options.timezone ?? "UTC",
    baseCurrency: options.baseCurrency ?? "PKR",
    importedAt: new Date().toISOString(),
  };

  return out;
}

function sideForModule(module: EntityModule): string {
  const sales = new Set(["customers", "invoices", "receipts"]);
  const purchases = new Set(["suppliers", "bills", "payments"]);
  if (sales.has(module)) return "sales";
  if (purchases.has(module)) return "purchases";
  if (module === "bank_transactions") return "bank";
  if (module === "products" || module === "stock_movements") return "inventory";
  return "general";
}

function dateFieldsForModule(module: EntityModule): string[] {
  const map: Partial<Record<EntityModule, string[]>> = {
    invoices: ["invoiceDate"],
    bills: ["billDate"],
    receipts: ["receiptDate"],
    payments: ["paymentDate"],
    bank_transactions: ["transactionDate"],
    stock_movements: ["movementDate"],
    journals: ["journalDate"],
  };
  return map[module] ?? [];
}

function decimalFieldsForModule(module: EntityModule): string[] {
  return ["totalAmount", "cost", "salePrice", "quantity", "rate", "openingBalance", "rate"];
}

function normalizeDecimal(value: unknown): string {
  const cleaned = String(value).replace(/,/g, "").replace(/[^\d.-]/g, "");
  return new Decimal(cleaned || 0).toFixed(4);
}
