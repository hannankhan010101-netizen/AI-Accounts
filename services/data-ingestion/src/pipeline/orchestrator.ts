import type { Prisma } from "@prisma/client";
import type { EntityModule, PipelineStage, StagingRecord } from "../types/pipeline.js";
import { STAGE_ORDER } from "../types/pipeline.js";
import { prisma } from "../lib/prisma.js";
import { config } from "../config.js";
import { applyMapping } from "../engines/mapping-engine.js";
import { validateBatch, hasBlockingErrors } from "../engines/validation-engine.js";
import { dedupeRecords, transformRow } from "../engines/transform-dedupe-engine.js";
import { reconcileBatch } from "../engines/reconciliation-engine.js";
import { TargetApiClient } from "../importers/target-api-client.js";
import { uploadErrorReportCsv } from "../storage/s3.js";
import { logger } from "../lib/logger.js";
import type { MappingRule } from "../types/pipeline.js";

export interface StageContext {
  migrationRunId: string;
  companyId: string;
  module: EntityModule;
  chunkIndex: number;
  accessToken?: string;
}

export async function processStage(
  stage: PipelineStage,
  ctx: StageContext,
): Promise<{ success: number; errors: number; skipped: number }> {
  const started = Date.now();
  let result = { success: 0, errors: 0, skipped: 0 };

  try {
    switch (stage) {
      case "validate":
        result = await runValidate(ctx);
        break;
      case "map":
        result = await runMap(ctx);
        break;
      case "transform":
        result = await runTransform(ctx);
        break;
      case "dedupe":
        result = await runDedupe(ctx);
        break;
      case "reconcile":
        result = await runReconcile(ctx);
        break;
      case "import":
        result = await runImport(ctx);
        break;
      case "verify":
        result = await runVerify(ctx);
        break;
      case "audit":
        result = await runAudit(ctx);
        break;
      default:
        logger.warn({ stage }, "extract handled separately");
    }
  } finally {
    await prisma.ingStageLog.create({
      data: {
        migrationRunId: ctx.migrationRunId,
        stage,
        chunkIndex: ctx.chunkIndex,
        status: result.errors > 0 ? "partial" : "completed",
        metrics: result,
        durationMs: Date.now() - started,
      },
    });
  }

  return result;
}

async function loadChunkRows(ctx: StageContext): Promise<StagingRecord[]> {
  const rows = await prisma.ingStagingRow.findMany({
    where: {
      migrationRunId: ctx.migrationRunId,
      chunkIndex: ctx.chunkIndex,
    },
    orderBy: { rowIndex: "asc" },
  });

  return rows.map((r) => ({
    rowIndex: r.rowIndex,
    chunkIndex: r.chunkIndex,
    sourceData: r.sourceData as Record<string, unknown>,
    mappedData: r.mappedData as Record<string, unknown> | undefined,
    transformedData: r.transformedData as Record<string, unknown> | undefined,
    fingerprint: r.fingerprint ?? undefined,
    externalId: r.externalId ?? undefined,
    isDuplicate: r.isDuplicate,
    isValid: r.isValid,
  }));
}

async function runValidate(ctx: StageContext) {
  const records = await loadChunkRows(ctx);
  const run = await prisma.ingMigrationRun.findUniqueOrThrow({
    where: { id: ctx.migrationRunId },
  });
  const issues = validateBatch(run.module as EntityModule, records);

  if (issues.length) {
    await prisma.ingValidationIssue.createMany({
      data: issues.map((i) => ({
        migrationRunId: ctx.migrationRunId,
        rowIndex: i.rowIndex,
        field: i.field,
        code: i.code,
        message: i.message,
        severity: i.severity,
        suggestedFix: i.suggestedFix,
      })),
    });
  }

  const blocking = hasBlockingErrors(issues);
  for (const record of records) {
    const rowIssues = issues.filter((i) => i.rowIndex === record.rowIndex);
    await prisma.ingStagingRow.updateMany({
      where: {
        migrationRunId: ctx.migrationRunId,
        rowIndex: record.rowIndex,
      },
      data: { isValid: !hasBlockingErrors(rowIssues) },
    });
  }

  return {
    success: records.filter((r) => !blocking).length,
    errors: issues.filter((i) => i.severity === "error").length,
    skipped: blocking ? records.length : 0,
  };
}

async function runMap(ctx: StageContext) {
  const run = await prisma.ingMigrationRun.findUniqueOrThrow({
    where: { id: ctx.migrationRunId },
    include: { mappingProfile: { include: { rules: true } } },
  });

  const rules: MappingRule[] =
    run.mappingProfile?.rules.map((r) => ({
      sourceField: r.sourceField,
      targetField: r.targetField,
      transform: r.transform ?? undefined,
      defaultValue: r.defaultValue ?? undefined,
      isRequired: r.isRequired,
    })) ?? [];

  const records = await loadChunkRows(ctx);
  let success = 0;

  for (const record of records) {
    const mapped = applyMapping(record.sourceData, rules);
    await prisma.ingStagingRow.updateMany({
      where: { migrationRunId: ctx.migrationRunId, rowIndex: record.rowIndex },
      data: { mappedData: mapped as Prisma.InputJsonValue },
    });
    success++;
  }

  return { success, errors: 0, skipped: 0 };
}

async function runTransform(ctx: StageContext) {
  const run = await prisma.ingMigrationRun.findUniqueOrThrow({
    where: { id: ctx.migrationRunId },
  });
  const options = (run.options as Record<string, unknown>) ?? {};
  const records = await loadChunkRows(ctx);
  let success = 0;

  for (const record of records) {
    const base = record.mappedData ?? record.sourceData;
    const transformed = transformRow(run.module as EntityModule, base, {
      timezone: String(options.timezone ?? "UTC"),
      baseCurrency: String(options.baseCurrency ?? "PKR"),
    });
    await prisma.ingStagingRow.updateMany({
      where: { migrationRunId: ctx.migrationRunId, rowIndex: record.rowIndex },
      data: { transformedData: transformed as Prisma.InputJsonValue },
    });
    success++;
  }

  return { success, errors: 0, skipped: 0 };
}

async function runDedupe(ctx: StageContext) {
  const run = await prisma.ingMigrationRun.findUniqueOrThrow({
    where: { id: ctx.migrationRunId },
  });
  const existing = await prisma.ingStagingRow.findMany({
    where: {
      migrationRunId: ctx.migrationRunId,
      fingerprint: { not: null },
      isDuplicate: false,
      chunkIndex: { lt: ctx.chunkIndex },
    },
    select: { fingerprint: true },
  });
  const fpSet = new Set(existing.map((e) => e.fingerprint!));
  const records = await loadChunkRows(ctx);
  const { records: deduped, duplicateCount } = dedupeRecords(
    run.module as EntityModule,
    records,
    fpSet,
  );

  for (const record of deduped) {
    await prisma.ingStagingRow.updateMany({
      where: { migrationRunId: ctx.migrationRunId, rowIndex: record.rowIndex },
      data: {
        fingerprint: record.fingerprint,
        isDuplicate: record.isDuplicate,
        externalId: record.externalId,
      },
    });
  }

  return {
    success: deduped.length - duplicateCount,
    errors: 0,
    skipped: duplicateCount,
  };
}

async function runReconcile(ctx: StageContext) {
  const run = await prisma.ingMigrationRun.findUniqueOrThrow({
    where: { id: ctx.migrationRunId },
  });
  const records = await loadChunkRows(ctx);
  const result = reconcileBatch(run.module as EntityModule, records);

  if (ctx.chunkIndex === 0) {
    await prisma.ingReconciliationReport.upsert({
      where: { migrationRunId: ctx.migrationRunId },
      create: {
        migrationRunId: ctx.migrationRunId,
        passed: result.passed,
        glBalanced: result.glBalanced,
        glDelta: result.glDelta,
        inventoryDelta: result.inventoryDelta,
        arTotal: result.arTotal,
        apTotal: result.apTotal,
        details: result.details as Prisma.InputJsonValue,
      },
      update: {
        passed: result.passed,
        glBalanced: result.glBalanced,
        glDelta: result.glDelta,
        details: result.details as Prisma.InputJsonValue,
      },
    });
  }

  return {
    success: result.passed ? records.length : 0,
    errors: result.passed ? 0 : 1,
    skipped: 0,
  };
}

async function runImport(ctx: StageContext) {
  const run = await prisma.ingMigrationRun.findUniqueOrThrow({
    where: { id: ctx.migrationRunId },
  });

  if (!ctx.accessToken) {
    return { success: 0, errors: 1, skipped: 0 };
  }

  const rows = await prisma.ingStagingRow.findMany({
    where: {
      migrationRunId: ctx.migrationRunId,
      chunkIndex: ctx.chunkIndex,
      isDuplicate: false,
      isValid: true,
      imported: false,
    },
  });

  const payload = rows.map(
    (r) => (r.transformedData ?? r.mappedData ?? r.sourceData) as Record<string, unknown>,
  );

  const client = new TargetApiClient(ctx.companyId, ctx.accessToken);
  const importResult = await client.importChunk(
    run.module as EntityModule,
    payload,
    run.options as Record<string, unknown>,
  );

  if (importResult.errors.length) {
    const csv = ["row,error", ...importResult.errors.map((e, i) => `${i + 1},"${e.replace(/"/g, '""')}"`)].join("\n");
    await uploadErrorReportCsv(ctx.companyId, ctx.migrationRunId, ctx.chunkIndex, csv);
  }

  for (const row of rows) {
    await prisma.ingStagingRow.update({
      where: { id: row.id },
      data: { imported: importResult.created > 0 },
    });
  }

  return {
    success: importResult.created,
    errors: importResult.errors.length,
    skipped: importResult.skipped,
  };
}

async function runVerify(ctx: StageContext) {
  const imported = await prisma.ingStagingRow.count({
    where: { migrationRunId: ctx.migrationRunId, imported: true },
  });
  const expected = await prisma.ingStagingRow.count({
    where: {
      migrationRunId: ctx.migrationRunId,
      isDuplicate: false,
      isValid: true,
    },
  });

  return {
    success: imported,
    errors: Math.max(0, expected - imported),
    skipped: 0,
  };
}

async function runAudit(ctx: StageContext) {
  await prisma.ingAuditEntry.create({
    data: {
      companyId: ctx.companyId,
      migrationRunId: ctx.migrationRunId,
      action: "chunk.audit.completed",
      details: { chunkIndex: ctx.chunkIndex },
    },
  });
  return { success: 1, errors: 0, skipped: 0 };
}

export async function enqueuePipelineForRun(
  migrationRunId: string,
  accessToken?: string,
): Promise<void> {
  const run = await prisma.ingMigrationRun.findUniqueOrThrow({
    where: { id: migrationRunId },
  });

  const chunkCount = Math.max(1, run.totalChunks);
  const { createQueue, QUEUE_NAMES, idempotencyKey } = await import("../queue/connection.js");
  const queue = createQueue(QUEUE_NAMES.pipeline);

  for (let chunkIndex = 0; chunkIndex < chunkCount; chunkIndex++) {
    for (const stage of STAGE_ORDER) {
      if (stage === "extract") continue;
      await queue.add(
        stage,
        {
          migrationRunId,
          companyId: run.companyId,
          stage,
          chunkIndex,
          accessToken,
        },
        {
          jobId: idempotencyKey(migrationRunId, stage, chunkIndex),
        },
      );
    }
  }

  await prisma.ingMigrationRun.update({
    where: { id: migrationRunId },
    data: { status: "validating", currentStage: "validate", startedAt: new Date() },
  });
}

export async function extractToStaging(
  migrationRunId: string,
  rows: Array<{ rowIndex: number; data: Record<string, unknown> }>,
): Promise<number> {
  const run = await prisma.ingMigrationRun.findUniqueOrThrow({
    where: { id: migrationRunId },
  });
  const chunkSize = run.chunkSize || config.CHUNK_SIZE;
  const chunks = Math.ceil(rows.length / chunkSize) || 1;

  await prisma.ingMigrationRun.update({
    where: { id: migrationRunId },
    data: {
      totalRows: rows.length,
      totalChunks: chunks,
      status: "extracting",
      currentStage: "extract",
    },
  });

  const batch: Prisma.IngStagingRowCreateManyInput[] = [];

  for (const row of rows) {
    const chunkIndex = Math.floor((row.rowIndex - 1) / chunkSize);
    batch.push({
      migrationRunId,
      companyId: run.companyId,
      rowIndex: row.rowIndex,
      chunkIndex,
      sourceData: row.data as Prisma.InputJsonValue,
    });
  }

  for (let i = 0; i < batch.length; i += 1000) {
    await prisma.ingStagingRow.createMany({ data: batch.slice(i, i + 1000) });
  }

  for (let c = 0; c < chunks; c++) {
    const rowStart = c * chunkSize + 1;
    const rowEnd = Math.min((c + 1) * chunkSize, rows.length);
    await prisma.ingMigrationChunk.create({
      data: {
        migrationRunId,
        chunkIndex: c,
        stage: "extract",
        rowStart,
        rowEnd,
        rowCount: rowEnd - rowStart + 1,
        idempotencyKey: `${migrationRunId}:extract:${c}`,
      },
    });
  }

  return rows.length;
}
