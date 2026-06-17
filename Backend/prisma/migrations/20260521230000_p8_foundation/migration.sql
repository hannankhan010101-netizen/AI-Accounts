-- P8: FBR retry fields on digital invoice submissions

ALTER TABLE "digital_invoice_submissions"
  ADD COLUMN IF NOT EXISTS "retry_count" INTEGER NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS "last_error" TEXT,
  ADD COLUMN IF NOT EXISTS "next_retry_at" TIMESTAMP(3);

CREATE INDEX IF NOT EXISTS "digital_invoice_submissions_company_id_status_retry_idx"
  ON "digital_invoice_submissions"("company_id", "status", "next_retry_at");
