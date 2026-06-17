/** Migration / data ingestion API — proxies to ingestion service in dev. */
import { getCurrentCompanyId } from "@/lib/auth/storage";

const INGESTION_BASE =
  typeof window !== "undefined"
    ? "/api/ingestion/v1"
    : process.env.INGESTION_API_URL ?? "http://127.0.0.1:4100/api/v1";

function path(suffix: string): string {
  const companyId = getCurrentCompanyId();
  if (!companyId) throw new Error("No company selected");
  return `${INGESTION_BASE}/companies/${companyId}/migrations${suffix}`;
}

function authHeaders(): Record<string, string> {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("accessToken") : null;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function ingestionFetch<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...init?.headers,
    },
  });
  if (!res.ok) {
    const err = (await res.json().catch(() => ({}))) as { message?: string; error?: string };
    throw new Error(err.message ?? err.error ?? res.statusText);
  }
  return res.json() as Promise<T>;
}

export type EntityModule =
  | "customers"
  | "suppliers"
  | "chart_of_accounts"
  | "invoices"
  | "bills"
  | "receipts"
  | "payments"
  | "products"
  | "stock_movements"
  | "journals"
  | "taxes"
  | "projects"
  | "bank_transactions";

export interface MigrationRun {
  id: string;
  name: string;
  module: EntityModule;
  status: string;
  totalRows: number;
  processedRows: number;
  successRows: number;
  errorRows: number;
  currentStage?: string | null;
  createdAt: string;
  [key: string]: unknown;
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
  type: string;
  required?: boolean;
}

export const migrationsApi = {
  list: () => ingestionFetch<{ result: MigrationRun[] }>(path("")),

  get: (runId: string) =>
    ingestionFetch<{ result: MigrationRun & { stageLogs?: unknown[]; validationIssues?: unknown[] } }>(
      path(`/runs/${runId}`),
    ),

  createRun: (body: {
    name: string;
    module: EntityModule;
    sourceType: string;
    sourceSystem?: string;
    sourceKey?: string;
    mappingProfileId?: string;
  }) =>
    ingestionFetch<{ result: MigrationRun }>(path("/runs"), {
      method: "POST",
      body: JSON.stringify(body),
    }),

  startRun: (runId: string) =>
    ingestionFetch<{ result: { started: boolean; rowCount: number } }>(
      path(`/runs/${runId}/start`),
      { method: "POST" },
    ),

  retryRun: (runId: string) =>
    ingestionFetch(path(`/runs/${runId}/retry`), { method: "POST" }),

  cancelRun: (runId: string) =>
    ingestionFetch(path(`/runs/${runId}/cancel`), { method: "POST" }),

  listMappingProfiles: () =>
    ingestionFetch<{ result: Array<{ id: string; name: string; module: EntityModule; rules: MappingRule[] }> }>(
      path("/mapping-profiles"),
    ),

  createMappingProfile: (body: {
    name: string;
    module: EntityModule;
    sourceSystem?: string;
    rules: MappingRule[];
  }) =>
    ingestionFetch(path("/mapping-profiles"), {
      method: "POST",
      body: JSON.stringify(body),
    }),

  suggestMappings: (profileId: string, sourceFields: string[], sourceSystem = "generic") =>
    ingestionFetch<{
      result: {
        suggestions: Array<{ sourceField: string; targetField: string; confidence: number; reason: string }>;
        proposedRules: MappingRule[];
      };
    }>(path(`/mapping-profiles/${profileId}/suggest`), {
      method: "POST",
      body: JSON.stringify({ sourceFields, sourceSystem }),
    }),

  getTargetSchema: (module: EntityModule) =>
    ingestionFetch<{ result: TargetFieldDef[] }>(path(`/target-schema/${module}`)),

  preview: (body: {
    module: EntityModule;
    rules: MappingRule[];
    rows: Record<string, unknown>[];
  }) =>
    ingestionFetch<{
      result: {
        preview: Array<{
          source: Record<string, unknown>;
          mapped: Record<string, unknown>;
          transformed: Record<string, unknown>;
          issues: Array<{ code: string; message: string; severity: string }>;
        }>;
        summary: { rowCount: number; errorCount: number; warningCount: number; valid: boolean };
      };
    }>(path("/preview"), { method: "POST", body: JSON.stringify(body) }),

  uploadCsv: async (runId: string, file: File) => {
    const companyId = getCurrentCompanyId();
    if (!companyId) throw new Error("No company selected");
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(
      `${INGESTION_BASE}/companies/${companyId}/migrations/runs/${runId}/upload`,
      {
        method: "POST",
        headers: authHeaders(),
        body: form,
      },
    );
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
};
