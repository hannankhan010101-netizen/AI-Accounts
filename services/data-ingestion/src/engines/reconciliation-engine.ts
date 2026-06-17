import { Decimal } from "decimal.js";
import type { EntityModule, ReconciliationResult, StagingRecord } from "../types/pipeline.js";

export function reconcileBatch(
  module: EntityModule,
  records: StagingRecord[],
): ReconciliationResult {
  const valid = records.filter((r) => !r.isDuplicate && r.isValid !== false);
  const details: Record<string, unknown> = {
    module,
    validRowCount: valid.length,
    duplicateCount: records.filter((r) => r.isDuplicate).length,
  };

  switch (module) {
    case "journals":
      return reconcileJournals(valid, details);
    case "invoices":
    case "receipts":
      return reconcileAr(valid, details);
    case "bills":
    case "payments":
      return reconcileAp(valid, details);
    case "stock_movements":
      return reconcileInventory(valid, details);
    default:
      return { passed: true, details };
  }
}

function reconcileJournals(
  records: StagingRecord[],
  details: Record<string, unknown>,
): ReconciliationResult {
  let totalDebit = new Decimal(0);
  let totalCredit = new Decimal(0);
  let imbalanced = 0;

  for (const record of records) {
    const data = record.transformedData ?? {};
    const lines = (data.lines as Record<string, unknown>[]) ?? [];
    let d = new Decimal(0);
    let c = new Decimal(0);
    for (const line of lines) {
      d = d.plus(String(line.debit ?? 0).replace(/,/g, "") || 0);
      c = c.plus(String(line.credit ?? 0).replace(/,/g, "") || 0);
    }
    if (d.minus(c).abs().gt(0.01)) imbalanced++;
    totalDebit = totalDebit.plus(d);
    totalCredit = totalCredit.plus(c);
  }

  const glDelta = totalDebit.minus(totalCredit).abs();
  const glBalanced = glDelta.lte(0.01) && imbalanced === 0;

  details.journalCount = records.length;
  details.imbalancedJournals = imbalanced;
  details.totalDebit = totalDebit.toFixed(4);
  details.totalCredit = totalCredit.toFixed(4);

  return {
    passed: glBalanced,
    glBalanced,
    glDelta: glDelta.toFixed(4),
    details,
  };
}

function reconcileAr(
  records: StagingRecord[],
  details: Record<string, unknown>,
): ReconciliationResult {
  const arTotal = sumField(records, "totalAmount");
  details.arTotal = arTotal;
  return { passed: true, arTotal, details };
}

function reconcileAp(
  records: StagingRecord[],
  details: Record<string, unknown>,
): ReconciliationResult {
  const apTotal = sumField(records, "totalAmount");
  details.apTotal = apTotal;
  return { passed: true, apTotal, details };
}

function reconcileInventory(
  records: StagingRecord[],
  details: Record<string, unknown>,
): ReconciliationResult {
  const byProduct = new Map<string, Decimal>();

  for (const record of records) {
    const data = record.transformedData ?? {};
    const code = String(data.productCode ?? "");
    const qty = new Decimal(String(data.quantity ?? 0).replace(/,/g, "") || 0);
    byProduct.set(code, (byProduct.get(code) ?? new Decimal(0)).plus(qty));
  }

  details.productMovementTotals = Object.fromEntries(
    [...byProduct.entries()].map(([k, v]) => [k, v.toFixed(4)]),
  );

  return { passed: true, inventoryDelta: "0", details };
}

function sumField(records: StagingRecord[], field: string): string {
  let total = new Decimal(0);
  for (const record of records) {
    const data = record.transformedData ?? record.mappedData ?? {};
    const val = data[field];
    if (val !== undefined) {
      total = total.plus(String(val).replace(/,/g, "") || 0);
    }
  }
  return total.toFixed(4);
}
