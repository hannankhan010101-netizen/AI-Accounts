-- Phase 2: external report row storage (blob) + optional S3 key

ALTER TABLE "report_runs"
  ADD COLUMN IF NOT EXISTS "storage_key" TEXT;

CREATE INDEX IF NOT EXISTS "idx_report_runs_company_status"
  ON "report_runs" ("company_id", "status", "created_at" DESC);
