import type { FastifyInstance } from "fastify";
import { z } from "zod";
import { requireTenantAccess, type TenantParams } from "../middleware/auth.js";
import { applyMapping } from "../../engines/mapping-engine.js";
import { validateBatch } from "../../engines/validation-engine.js";
import { transformRow } from "../../engines/transform-dedupe-engine.js";
import { config } from "../../config.js";
import { EntityModuleSchema } from "../../types/pipeline.js";
import type { MappingRule, StagingRecord } from "../../types/pipeline.js";

export async function previewRoutes(app: FastifyInstance) {
  app.addHook("preHandler", requireTenantAccess);

  app.post<{ Params: TenantParams }>("/preview", async (request) => {
    const body = z
      .object({
        module: EntityModuleSchema,
        rules: z.array(
          z.object({
            sourceField: z.string(),
            targetField: z.string(),
            transform: z.string().optional(),
            defaultValue: z.string().optional(),
            isRequired: z.boolean().optional(),
          }),
        ),
        rows: z.array(z.record(z.unknown())).max(config.MAX_PREVIEW_ROWS),
      })
      .parse(request.body);

    const rules = body.rules as MappingRule[];
    const preview: Array<{
      source: Record<string, unknown>;
      mapped: Record<string, unknown>;
      transformed: Record<string, unknown>;
      issues: ReturnType<typeof validateBatch>;
    }> = [];

    const staging: StagingRecord[] = [];

    for (let i = 0; i < body.rows.length; i++) {
      const source = body.rows[i];
      const mapped = applyMapping(source, rules);
      const transformed = transformRow(body.module, mapped);
      staging.push({
        rowIndex: i + 1,
        chunkIndex: 0,
        sourceData: source,
        mappedData: mapped,
        transformedData: transformed,
      });
      preview.push({
        source,
        mapped,
        transformed,
        issues: [],
      });
    }

    const batchIssues = validateBatch(body.module, staging);
    for (const item of preview) {
      item.issues = batchIssues.filter((iss) => {
        const idx = preview.indexOf(item) + 1;
        return iss.rowIndex === undefined || iss.rowIndex === idx;
      });
    }

    const errorCount = batchIssues.filter((i) => i.severity === "error").length;
    const warningCount = batchIssues.filter((i) => i.severity === "warning").length;

    return {
      result: {
        preview,
        summary: {
          rowCount: body.rows.length,
          errorCount,
          warningCount,
          valid: errorCount === 0,
        },
      },
    };
  });
}
