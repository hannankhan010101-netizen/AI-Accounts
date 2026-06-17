import type { Job } from "bullmq";
import {
  createWorker,
  QUEUE_NAMES,
  type PipelineJobData,
} from "../queue/connection.js";
import { processStage } from "../pipeline/orchestrator.js";
import type { PipelineStage } from "../types/pipeline.js";
import { prisma } from "../lib/prisma.js";
import { logger } from "../lib/logger.js";

export function startPipelineWorker(): void {
  createWorker(QUEUE_NAMES.pipeline, handlePipelineJob, 4);

  logger.info("Pipeline worker started");
}

async function handlePipelineJob(job: Job<PipelineJobData>): Promise<void> {
  const { migrationRunId, companyId, stage, chunkIndex, accessToken } = job.data;

  const chunk = await prisma.ingMigrationChunk.findUnique({
    where: {
      migrationRunId_chunkIndex_stage: {
        migrationRunId,
        chunkIndex,
        stage: stage as PipelineStage,
      },
    },
  });

  if (chunk?.status === "completed") {
    logger.info({ jobId: job.id }, "Skipping completed chunk (idempotent)");
    return;
  }

  await prisma.ingMigrationChunk.upsert({
    where: {
      migrationRunId_chunkIndex_stage: {
        migrationRunId,
        chunkIndex,
        stage: stage as PipelineStage,
      },
    },
    create: {
      migrationRunId,
      chunkIndex,
      stage: stage as PipelineStage,
      rowStart: 0,
      rowEnd: 0,
      idempotencyKey: job.id ?? `${migrationRunId}:${stage}:${chunkIndex}`,
      status: "processing",
      startedAt: new Date(),
      attempts: 1,
    },
    update: {
      status: "processing",
      attempts: { increment: 1 },
      startedAt: new Date(),
    },
  });

  await prisma.ingMigrationRun.update({
    where: { id: migrationRunId },
    data: { currentStage: stage as PipelineStage, status: mapStatus(stage) },
  });

  const result = await processStage(stage as PipelineStage, {
    migrationRunId,
    companyId,
    module: (await prisma.ingMigrationRun.findUniqueOrThrow({ where: { id: migrationRunId } }))
      .module as import("../types/pipeline.js").EntityModule,
    chunkIndex,
    accessToken,
  });

  await prisma.ingMigrationChunk.updateMany({
    where: {
      migrationRunId,
      chunkIndex,
      stage: stage as PipelineStage,
    },
    data: {
      status: result.errors > 0 ? "failed" : "completed",
      successCount: result.success,
      errorCount: result.errors,
      completedAt: new Date(),
      lastError: result.errors > 0 ? `${result.errors} errors` : null,
    },
  });

  await prisma.ingMigrationRun.update({
    where: { id: migrationRunId },
    data: {
      processedRows: { increment: result.success + result.skipped },
      successRows: { increment: result.success },
      errorRows: { increment: result.errors },
      skippedRows: { increment: result.skipped },
      completedChunks: { increment: 1 },
    },
  });

  if (stage === "audit") {
    const run = await prisma.ingMigrationRun.findUniqueOrThrow({
      where: { id: migrationRunId },
    });
    if (run.completedChunks >= run.totalChunks * 8) {
      await prisma.ingMigrationRun.update({
        where: { id: migrationRunId },
        data: { status: "completed", completedAt: new Date(), currentStage: null },
      });
    }
  }
}

function mapStatus(stage: string): import("@prisma/client").MigrationStatus {
  const map: Record<string, import("@prisma/client").MigrationStatus> = {
    validate: "validating",
    map: "mapping",
    transform: "transforming",
    dedupe: "deduping",
    reconcile: "reconciling",
    import: "importing",
    verify: "verifying",
    audit: "completed",
  };
  return map[stage] ?? "pending";
}
