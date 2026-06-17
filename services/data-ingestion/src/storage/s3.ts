import {
  S3Client,
  PutObjectCommand,
  GetObjectCommand,
} from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";
import { createCipheriv, createDecipheriv, randomBytes, scryptSync } from "node:crypto";
import { config } from "../config.js";

let s3: S3Client | null = null;

function getS3(): S3Client {
  if (!s3) {
    s3 = new S3Client({
      region: config.S3_REGION,
      endpoint: config.S3_ENDPOINT,
      forcePathStyle: true,
      credentials:
        config.S3_ACCESS_KEY && config.S3_SECRET_KEY
          ? {
              accessKeyId: config.S3_ACCESS_KEY,
              secretAccessKey: config.S3_SECRET_KEY,
            }
          : undefined,
    });
  }
  return s3;
}

export function tenantS3Key(
  companyId: string,
  migrationRunId: string,
  ...parts: string[]
): string {
  return ["tenants", companyId, "migrations", migrationRunId, ...parts].join("/");
}

export async function presignUpload(
  key: string,
  contentType: string,
  expiresIn = 900,
): Promise<string> {
  const command = new PutObjectCommand({
    Bucket: config.S3_BUCKET,
    Key: key,
    ContentType: contentType,
  });
  return getSignedUrl(getS3(), command, { expiresIn });
}

export async function uploadBuffer(
  key: string,
  body: Buffer,
  contentType: string,
): Promise<void> {
  await getS3().send(
    new PutObjectCommand({
      Bucket: config.S3_BUCKET,
      Key: key,
      Body: body,
      ContentType: contentType,
    }),
  );
}

export async function downloadBuffer(key: string): Promise<Buffer> {
  const res = await getS3().send(
    new GetObjectCommand({ Bucket: config.S3_BUCKET, Key: key }),
  );
  const stream = res.Body;
  if (!stream) throw new Error("Empty S3 body");
  const chunks: Buffer[] = [];
  for await (const chunk of stream as AsyncIterable<Buffer>) {
    chunks.push(Buffer.from(chunk));
  }
  return Buffer.concat(chunks);
}

export function encryptBuffer(plaintext: Buffer): Buffer {
  const key = deriveKey();
  const iv = randomBytes(12);
  const cipher = createCipheriv("aes-256-gcm", key, iv);
  const encrypted = Buffer.concat([cipher.update(plaintext), cipher.final()]);
  const tag = cipher.getAuthTag();
  return Buffer.concat([iv, tag, encrypted]);
}

export function decryptBuffer(payload: Buffer): Buffer {
  const key = deriveKey();
  const iv = payload.subarray(0, 12);
  const tag = payload.subarray(12, 28);
  const encrypted = payload.subarray(28);
  const decipher = createDecipheriv("aes-256-gcm", key, iv);
  decipher.setAuthTag(tag);
  return Buffer.concat([decipher.update(encrypted), decipher.final()]);
}

function deriveKey(): Buffer {
  const secret = config.FILE_ENCRYPTION_KEY ?? "dev-only-insecure-key-change-me!!";
  return scryptSync(secret, "ingestion-salt", 32);
}

export async function uploadErrorReportCsv(
  companyId: string,
  runId: string,
  chunkIndex: number,
  csv: string,
): Promise<string> {
  const key = tenantS3Key(companyId, runId, "errors", `chunk-${chunkIndex}.csv`);
  await uploadBuffer(key, Buffer.from(csv, "utf-8"), "text/csv");
  return key;
}
