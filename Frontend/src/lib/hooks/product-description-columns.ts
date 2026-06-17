/** Product description column config — Smart Settings §12.2.5. */

export type ProductDescriptionDocType = "SI" | "VI" | "SC" | "VC" | "PO" | "SO" | "SQ";

export interface ProductDescriptionColumn {
  fieldKey: string;
  header: string;
  width?: string;
  fillFromProductName?: boolean;
}

function fieldKeyFromDisplayName(displayName: string, index: number): string {
  const normalized = displayName.trim().toLowerCase();
  if (normalized.includes("product") && normalized.includes("desc")) {
    return "description";
  }
  const textMatch = /^text\s*(\d+)$/i.exec(displayName.trim());
  if (textMatch) {
    return `text${textMatch[1]}`;
  }
  return `desc${index + 1}`;
}

function matchesDocType(transactionTypes: string | undefined, docType: ProductDescriptionDocType): boolean {
  if (!transactionTypes?.trim()) return true;
  const tokens = transactionTypes
    .split(/[,;\s]+/)
    .map((t) => t.trim().toUpperCase())
    .filter(Boolean);
  return tokens.includes(docType);
}

export function parseProductDescriptionColumns(
  rows: unknown,
  docType: ProductDescriptionDocType,
): ProductDescriptionColumn[] {
  if (!Array.isArray(rows)) return [];

  const columns: ProductDescriptionColumn[] = [];
  rows.forEach((row, index) => {
    if (!row || typeof row !== "object") return;
    const displayName = "displayName" in row ? String(row.displayName ?? "") : "";
    const label = "label" in row ? String(row.label ?? "") : displayName;
    const transactionTypes =
      "transactionTypes" in row ? String(row.transactionTypes ?? "") : undefined;
    const width = "width" in row && row.width ? String(row.width) : undefined;

    if (!displayName.trim() && !label.trim()) return;
    if (!matchesDocType(transactionTypes, docType)) return;

    const fieldKey = fieldKeyFromDisplayName(displayName || label, index);
    columns.push({
      fieldKey,
      header: label.trim() || displayName.trim(),
      width,
      fillFromProductName: fieldKey === "description",
    });
  });

  return columns;
}

/** Spread stored description fields onto a form line row. */
export function descriptionFieldsToFormLine(line: Record<string, unknown>): Record<string, string> {
  const out: Record<string, string> = {};
  const df = line.descriptionFields;
  if (df && typeof df === "object" && !Array.isArray(df)) {
    for (const [key, val] of Object.entries(df as Record<string, unknown>)) {
      if (typeof val === "string") out[key] = val;
    }
  }
  if (typeof line.description === "string" && line.description.trim()) {
    out.description = line.description.trim();
  }
  return out;
}

export function lineDescriptionCellValue(
  line: Record<string, unknown>,
  fieldKey: string,
): string {
  if (fieldKey === "description") {
    const direct = line.description;
    if (typeof direct === "string" && direct.trim()) return direct.trim();
  }
  const df = line.descriptionFields;
  if (df && typeof df === "object" && !Array.isArray(df)) {
    const val = (df as Record<string, unknown>)[fieldKey];
    if (typeof val === "string" && val.trim()) return val.trim();
  }
  const direct = line[fieldKey];
  return typeof direct === "string" && direct.trim() ? direct.trim() : "—";
}

export function descriptionFieldsFromLine(
  line: Record<string, unknown>,
  columns: ProductDescriptionColumn[],
): Record<string, string> | undefined {
  const out: Record<string, string> = {};
  for (const col of columns) {
    if (col.fieldKey === "description") continue;
    const val = line[col.fieldKey];
    if (typeof val === "string" && val.trim()) {
      out[col.fieldKey] = val.trim();
    }
  }
  return Object.keys(out).length > 0 ? out : undefined;
}
