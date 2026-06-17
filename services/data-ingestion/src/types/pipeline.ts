import { z } from "zod";

export const EntityModuleSchema = z.enum([
  "customers",
  "suppliers",
  "chart_of_accounts",
  "invoices",
  "bills",
  "receipts",
  "payments",
  "products",
  "stock_movements",
  "journals",
  "taxes",
  "projects",
  "bank_transactions",
]);

export type EntityModule = z.infer<typeof EntityModuleSchema>;

export const PipelineStageSchema = z.enum([
  "extract",
  "validate",
  "map",
  "transform",
  "dedupe",
  "reconcile",
  "import",
  "verify",
  "audit",
]);

export type PipelineStage = z.infer<typeof PipelineStageSchema>;

export const STAGE_ORDER: PipelineStage[] = [
  "extract",
  "validate",
  "map",
  "transform",
  "dedupe",
  "reconcile",
  "import",
  "verify",
  "audit",
];

/** FK-safe import order across modules in a full migration batch. */
export const MODULE_IMPORT_ORDER: EntityModule[] = [
  "chart_of_accounts",
  "taxes",
  "projects",
  "customers",
  "suppliers",
  "products",
  "invoices",
  "bills",
  "receipts",
  "payments",
  "bank_transactions",
  "stock_movements",
  "journals",
];

export interface StagingRecord {
  rowIndex: number;
  chunkIndex: number;
  sourceData: Record<string, unknown>;
  mappedData?: Record<string, unknown>;
  transformedData?: Record<string, unknown>;
  fingerprint?: string;
  externalId?: string;
  isDuplicate?: boolean;
  isValid?: boolean;
}

export interface ValidationIssue {
  rowIndex?: number;
  field?: string;
  code: string;
  message: string;
  severity: "error" | "warning" | "info";
  suggestedFix?: string;
}

export interface ChunkResult {
  successCount: number;
  errorCount: number;
  skippedCount: number;
  duplicateCount: number;
  errors: ValidationIssue[];
}

export interface MappingRule {
  sourceField: string;
  targetField: string;
  transform?: string;
  defaultValue?: string;
  isRequired?: boolean;
}

export interface TargetFieldDef {
  field: string;
  label: string;
  type: "string" | "number" | "decimal" | "date" | "boolean" | "enum";
  required?: boolean;
  enumValues?: string[];
  description?: string;
}

export interface ReconciliationResult {
  passed: boolean;
  glBalanced?: boolean;
  glDelta?: string;
  inventoryDelta?: string;
  arTotal?: string;
  apTotal?: string;
  details: Record<string, unknown>;
}

export interface ImportContext {
  companyId: string;
  migrationRunId: string;
  module: EntityModule;
  sourceSystem: string;
  chunkIndex: number;
  options: Record<string, unknown>;
}
