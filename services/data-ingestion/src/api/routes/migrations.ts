import type { FastifyInstance, FastifyRequest } from "fastify";
import type { Prisma } from "@prisma/client";
import { z } from "zod";
import { prisma } from "../../lib/prisma.js";
import {
  extractToStaging,
  enqueuePipelineForRun,
} from "../../pipeline/orchestrator.js";
import { requireTenantAccess, getAccessToken, type TenantParams } from "../middleware/auth.js";
import { presignUpload, tenantS3Key } from "../../storage/s3.js";
import { streamCsv, collectRows } from "../../extractors/csv-stream.js";
import { streamFastAccountsLabeled } from "../../extractors/fastaccounts-adapter.js";
import { EntityModuleSchema } from "../../types/pipeline.js";
import { writeFile, unlink, mkdtemp } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

const CreateRunSchema = z.object({
  name: z.string().min(1),
  module: EntityModuleSchema,
  mode: z.enum(["batch", "incremental", "webhook", "api_pull"]).default("batch"),
  sourceType: z.enum(["csv", "xlsx", "json", "api", "webhook", "fastaccounts"]),
  sourceSystem: z.string().default("generic"),
  mappingProfileId: z.string().optional(),
  sourceKey: z.string().optional(),
  options: z.record(z.unknown()).default({}),
  idempotencyKey: z.string().optional(),
});

export async function migrationRoutes(app: FastifyInstance) {
  app.addHook("preHandler", requireTenantAccess);

  app.get("/", async (request: FastifyRequest<{ Params: TenantParams }>) => {
    const runs = await prisma.ingMigrationRun.findMany({
      where: { companyId: request.params.companyId },
      orderBy: { createdAt: "desc" },
      take: 50,
    });
    return { result: runs };
  });

  app.get<{ Params: TenantParams & { runId: string } }>(
    "/runs/:runId",
    async (request) => {
      const run = await prisma.ingMigrationRun.findFirst({
        where: { id: request.params.runId, companyId: request.params.companyId },
        include: {
          stageLogs: { orderBy: { createdAt: "desc" }, take: 100 },
          validationIssues: { where: { severity: "error" }, take: 200 },
          reconciliation: true,
        },
      });
      if (!run) throw Object.assign(new Error("Not found"), { statusCode: 404 });
      return { result: run };
    },
  );

  app.post<{ Params: TenantParams }>("/runs", async (request, reply) => {
    const body = CreateRunSchema.parse(request.body);
    const run = await prisma.ingMigrationRun.create({
      data: {
        companyId: request.params.companyId,
        name: body.name,
        module: body.module,
        mode: body.mode,
        sourceType: body.sourceType,
        sourceSystem: body.sourceSystem,
        mappingProfileId: body.mappingProfileId,
        sourceKey: body.sourceKey,
        options: body.options as Prisma.InputJsonValue,
        idempotencyKey: body.idempotencyKey,
      },
    });
    reply.code(201);
    return { result: run };
  });

  app.post<{ Params: TenantParams & { runId: string } }>(
    "/runs/:runId/start",
    async (request) => {
      const run = await prisma.ingMigrationRun.findFirst({
        where: { id: request.params.runId, companyId: request.params.companyId },
      });
      if (!run) throw Object.assign(new Error("Not found"), { statusCode: 404 });

      let rows: Array<{ rowIndex: number; data: Record<string, unknown> }> = [];

      if (run.sourceType === "fastaccounts" && run.sourceKey) {
        for await (const row of streamFastAccountsLabeled(run.sourceKey, run.module as z.infer<typeof EntityModuleSchema>)) {
          rows.push({ rowIndex: row.rowIndex, data: row.data });
        }
      } else if (run.sourceKey?.endsWith(".csv")) {
        const streamRows = await collectRows(streamCsv(run.sourceKey));
        rows = streamRows.map((r) => ({ rowIndex: r.rowIndex, data: r.data }));
      }

      await extractToStaging(run.id, rows);
      await enqueuePipelineForRun(run.id, getAccessToken(request));

      return { result: { started: true, rowCount: rows.length } };
    },
  );

  app.post<{ Params: TenantParams }>("/uploads/presign", async (request) => {
    const body = z
      .object({
        runId: z.string(),
        fileName: z.string(),
        contentType: z.string(),
      })
      .parse(request.body);

    const key = tenantS3Key(
      request.params.companyId,
      body.runId,
      "source",
      body.fileName,
    );
    const url = await presignUpload(key, body.contentType);
    return { result: { uploadUrl: url, key } };
  });

  app.post<{ Params: TenantParams & { runId: string } }>(
    "/runs/:runId/upload",
    async (request) => {
      const data = await request.file();
      if (!data) throw Object.assign(new Error("No file"), { statusCode: 400 });

      const dir = await mkdtemp(join(tmpdir(), "ing-"));
      const tmpPath = join(dir, data.filename);
      const buffer = await data.toBuffer();
      await writeFile(tmpPath, buffer);

      const streamRows = await collectRows(streamCsv(tmpPath));
      const rows = streamRows.map((r) => ({ rowIndex: r.rowIndex, data: r.data }));
      await extractToStaging(request.params.runId, rows);
      await enqueuePipelineForRun(request.params.runId, getAccessToken(request));

      await unlink(tmpPath).catch(() => undefined);

      return { result: { rowCount: rows.length } };
    },
  );

  app.post<{ Params: TenantParams & { runId: string } }>(
    "/runs/:runId/retry",
    async (request) => {
      await enqueuePipelineForRun(request.params.runId, getAccessToken(request));
      return { result: { retried: true } };
    },
  );

  app.post<{ Params: TenantParams & { runId: string } }>(
    "/runs/:runId/cancel",
    async (request) => {
      await prisma.ingMigrationRun.updateMany({
        where: { id: request.params.runId, companyId: request.params.companyId },
        data: { status: "cancelled" },
      });
      return { result: { cancelled: true } };
    },
  );
}
