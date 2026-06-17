import { Queue, Worker, type Job } from "bullmq";
import { Redis } from "ioredis";
import { config } from "../config.js";

export const QUEUE_NAMES = {
  orchestrator: "migration-orchestrator",
  pipeline: "migration-pipeline",
} as const;

let connection: Redis | null = null;

export function getRedisConnection(): Redis {
  if (!connection) {
    connection = new Redis(config.REDIS_URL, { maxRetriesPerRequest: null });
  }
  return connection;
}

export function createQueue(name: string): Queue {
  return new Queue(name, {
    connection: getRedisConnection(),
    defaultJobOptions: {
      attempts: 5,
      backoff: { type: "exponential", delay: 3000 },
      removeOnComplete: { count: 1000 },
      removeOnFail: { count: 5000 },
    },
  });
}

export function createWorker(
  name: string,
  processor: (job: Job) => Promise<void>,
  concurrency = 4,
): Worker {
  return new Worker(name, processor, {
    connection: getRedisConnection(),
    concurrency,
  });
}

export interface PipelineJobData {
  migrationRunId: string;
  companyId: string;
  stage: string;
  chunkIndex: number;
  accessToken?: string;
}

export function idempotencyKey(
  runId: string,
  stage: string,
  chunkIndex: number,
): string {
  return `${runId}:${stage}:${chunkIndex}`;
}
