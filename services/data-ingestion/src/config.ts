import { z } from "zod";

const envSchema = z.object({
  DATABASE_URL: z.string().min(1),
  REDIS_URL: z.string().default("redis://localhost:6379"),
  BACKEND_API_URL: z.string().default("http://127.0.0.1:8000"),
  BACKEND_SERVICE_TOKEN: z.string().optional(),
  S3_ENDPOINT: z.string().optional(),
  S3_REGION: z.string().default("us-east-1"),
  S3_BUCKET: z.string().default("ai-accounts-imports"),
  S3_ACCESS_KEY: z.string().optional(),
  S3_SECRET_KEY: z.string().optional(),
  PORT: z.coerce.number().default(4100),
  NODE_ENV: z.enum(["development", "production", "test"]).default("development"),
  CHUNK_SIZE: z.coerce.number().default(500),
  MAX_PREVIEW_ROWS: z.coerce.number().default(100),
  FILE_ENCRYPTION_KEY: z.string().optional(),
  AI_MAPPING_URL: z.string().optional(),
  AI_MAPPING_API_KEY: z.string().optional(),
});

export type Config = z.infer<typeof envSchema>;

export function loadConfig(): Config {
  return envSchema.parse(process.env);
}

export const config = loadConfig();
