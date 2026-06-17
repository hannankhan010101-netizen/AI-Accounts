import { Decimal } from "decimal.js";
import type { EntityModule, StagingRecord, ValidationIssue } from "../types/pipeline.js";
import { getTargetSchema } from "../domain/target-schemas.js";

const DATE_PATTERNS = [
  /^(\d{4})-(\d{2})-(\d{2})/,
  /^(\d{2})\/(\d{2})\/(\d{4})/,
  /^(\d{2})-(\d{2})-(\d{4})/,
];

export function validateRow(
  module: EntityModule,
  rowIndex: number,
  data: Record<string, unknown>,
): ValidationIssue[] {
  const issues: ValidationIssue[] = [];
  const schema = getTargetSchema(module);

  for (const field of schema) {
    const value = data[field.field];

    if (field.required && (value === undefined || value === null || value === "")) {
      issues.push({
        rowIndex,
        field: field.field,
        code: "REQUIRED",
        message: `${field.label} is required`,
        severity: "error",
        suggestedFix: `Map a source column to ${field.field}`,
      });
      continue;
    }

    if (value === undefined || value === null || value === "") continue;

    switch (field.type) {
      case "decimal":
        if (!isValidDecimal(value)) {
          issues.push({
            rowIndex,
            field: field.field,
            code: "INVALID_DECIMAL",
            message: `${field.label} must be a valid number`,
            severity: "error",
            suggestedFix: "Remove commas or currency symbols",
          });
        }
        break;
      case "number":
        if (Number.isNaN(Number(value))) {
          issues.push({
            rowIndex,
            field: field.field,
            code: "INVALID_NUMBER",
            message: `${field.label} must be numeric`,
            severity: "error",
          });
        }
        break;
      case "date":
        if (!parseDate(String(value))) {
          issues.push({
            rowIndex,
            field: field.field,
            code: "INVALID_DATE",
            message: `${field.label} is not a valid date`,
            severity: "error",
            suggestedFix: "Use YYYY-MM-DD or DD/MM/YYYY",
          });
        }
        break;
      case "enum":
        if (field.enumValues && !field.enumValues.includes(String(value).toLowerCase())) {
          issues.push({
            rowIndex,
            field: field.field,
            code: "INVALID_ENUM",
            message: `${field.label} must be one of: ${field.enumValues.join(", ")}`,
            severity: "warning",
          });
        }
        break;
      case "boolean":
        break;
      default:
        if (String(value).length > 500) {
          issues.push({
            rowIndex,
            field: field.field,
            code: "STRING_TOO_LONG",
            message: `${field.label} exceeds 500 characters`,
            severity: "warning",
          });
        }
    }
  }

  if (module === "journals" && Array.isArray(data.lines)) {
    issues.push(...validateJournalLines(rowIndex, data.lines as Record<string, unknown>[]));
  }

  return issues;
}

export function validateBatch(
  module: EntityModule,
  records: StagingRecord[],
): ValidationIssue[] {
  const issues: ValidationIssue[] = [];
  const codes = new Map<string, number>();

  for (const record of records) {
    const data = record.mappedData ?? record.sourceData;
    issues.push(...validateRow(module, record.rowIndex, data));

    const codeField = codeFieldForModule(module);
    if (codeField) {
      const code = String(data[codeField] ?? "").trim().toLowerCase();
      if (code) {
        codes.set(code, (codes.get(code) ?? 0) + 1);
      }
    }
  }

  for (const [code, count] of codes) {
    if (count > 1) {
      issues.push({
        code: "DUPLICATE_CODE_IN_BATCH",
        message: `Code "${code}" appears ${count} times in this batch`,
        severity: "warning",
        suggestedFix: "Enable deduplication or fix source data",
      });
    }
  }

  return issues;
}

function validateJournalLines(
  rowIndex: number,
  lines: Record<string, unknown>[],
): ValidationIssue[] {
  const issues: ValidationIssue[] = [];
  let debitSum = new Decimal(0);
  let creditSum = new Decimal(0);

  for (const line of lines) {
    debitSum = debitSum.plus(parseDecimal(line.debit) ?? 0);
    creditSum = creditSum.plus(parseDecimal(line.credit) ?? 0);
  }

  const delta = debitSum.minus(creditSum).abs();
  if (delta.gt(0.01)) {
    issues.push({
      rowIndex,
      code: "GL_IMBALANCE",
      message: `Journal debits (${debitSum}) ≠ credits (${creditSum})`,
      severity: "error",
      suggestedFix: "Adjust line amounts so debits equal credits",
    });
  }

  if (lines.length < 2) {
    issues.push({
      rowIndex,
      code: "JOURNAL_MIN_LINES",
      message: "Journal must have at least 2 lines",
      severity: "error",
    });
  }

  return issues;
}

function codeFieldForModule(module: EntityModule): string | null {
  const map: Partial<Record<EntityModule, string>> = {
    customers: "code",
    suppliers: "code",
    products: "code",
    projects: "code",
    chart_of_accounts: "code",
  };
  return map[module] ?? null;
}

function isValidDecimal(value: unknown): boolean {
  return parseDecimal(value) !== null;
}

function parseDecimal(value: unknown): Decimal | null {
  try {
    const cleaned = String(value).replace(/,/g, "").replace(/[^\d.-]/g, "");
    if (!cleaned) return null;
    return new Decimal(cleaned);
  } catch {
    return null;
  }
}

export function parseDate(value: string): Date | null {
  for (const pattern of DATE_PATTERNS) {
    const m = value.match(pattern);
    if (!m) continue;
    if (pattern === DATE_PATTERNS[0]) {
      return new Date(Date.UTC(+m[1], +m[2] - 1, +m[3]));
    }
    return new Date(Date.UTC(+m[3], +m[2] - 1, +m[1]));
  }
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? null : d;
}

export function hasBlockingErrors(issues: ValidationIssue[]): boolean {
  return issues.some((i) => i.severity === "error");
}
