import { config } from "../config.js";
import { logger } from "../lib/logger.js";
import type { EntityModule } from "../types/pipeline.js";

export interface ImportResult {
  created: number;
  skipped: number;
  errors: string[];
  targetIds: string[];
}

const MODULE_TO_JOB_TYPE: Partial<Record<EntityModule, string>> = {
  customers: "customers",
  products: "products",
  bank_transactions: "bank_payments",
};

export class TargetApiClient {
  constructor(
    private readonly companyId: string,
    private readonly accessToken: string,
  ) {}

  private url(path: string): string {
    return `${config.BACKEND_API_URL}/api/v1/companies/${this.companyId}${path}`;
  }

  private headers(): Record<string, string> {
    const h: Record<string, string> = {
      "Content-Type": "application/json",
      Authorization: `Bearer ${this.accessToken}`,
    };
    if (config.BACKEND_SERVICE_TOKEN) {
      h["X-Service-Token"] = config.BACKEND_SERVICE_TOKEN;
    }
    return h;
  }

  async importChunk(
    module: EntityModule,
    rows: Record<string, unknown>[],
    options: Record<string, unknown> = {},
  ): Promise<ImportResult> {
    const jobType = MODULE_TO_JOB_TYPE[module];

    if (jobType) {
      return this.enqueueImportJob(jobType, rows, options);
    }

    return this.importViaEntityEndpoint(module, rows);
  }

  private async enqueueImportJob(
    jobType: string,
    rows: Record<string, unknown>[],
    options: Record<string, unknown>,
  ): Promise<ImportResult> {
    const res = await fetch(this.url("/import-jobs"), {
      method: "POST",
      headers: this.headers(),
      body: JSON.stringify({
        jobType,
        rows,
        options: { skipExisting: true, ...options },
      }),
    });

    if (!res.ok) {
      const err = await res.text();
      logger.error({ status: res.status, err }, "import job enqueue failed");
      return { created: 0, skipped: rows.length, errors: [err], targetIds: [] };
    }

    const body = (await res.json()) as { result?: { id?: string } };
    return {
      created: rows.length,
      skipped: 0,
      errors: [],
      targetIds: body.result?.id ? [body.result.id] : [],
    };
  }

  private async importViaEntityEndpoint(
    module: EntityModule,
    rows: Record<string, unknown>[],
  ): Promise<ImportResult> {
    const endpoint = entityEndpoint(module);
    if (!endpoint) {
      return {
        created: 0,
        skipped: rows.length,
        errors: [`No target endpoint for module: ${module}`],
        targetIds: [],
      };
    }

    const result: ImportResult = { created: 0, skipped: 0, errors: [], targetIds: [] };

    for (const row of rows) {
      try {
        const res = await fetch(this.url(endpoint), {
          method: "POST",
          headers: this.headers(),
          body: JSON.stringify(mapRowToPayload(module, row)),
        });
        if (res.ok) {
          const body = (await res.json()) as { result?: { id?: string } };
          result.created++;
          if (body.result?.id) result.targetIds.push(body.result.id);
        } else {
          result.skipped++;
          result.errors.push(await res.text());
        }
      } catch (e) {
        result.skipped++;
        result.errors.push(String(e));
      }
    }

    return result;
  }
}

function entityEndpoint(module: EntityModule): string | null {
  const map: Partial<Record<EntityModule, string>> = {
    customers: "/customers",
    suppliers: "/suppliers",
    products: "/products",
    projects: "/projects",
    invoices: "/sales/invoices",
    bills: "/purchases/bills",
    receipts: "/sales/receipts",
    payments: "/purchases/payments",
  };
  return map[module] ?? null;
}

function mapRowToPayload(
  module: EntityModule,
  row: Record<string, unknown>,
): Record<string, unknown> {
  const meta = row._meta as Record<string, unknown> | undefined;
  const { _meta: _, ...rest } = row;
  void meta;
  void _;
  return rest;
}
