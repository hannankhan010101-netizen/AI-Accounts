-- P3: approval requests, journal line nominal FK

CREATE TABLE IF NOT EXISTS "approval_requests" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "entity_type" TEXT NOT NULL,
    "entity_id" TEXT NOT NULL,
    "amount" DECIMAL(18,4) NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'pending',
    "requested_by_id" TEXT,
    "approved_by_id" TEXT,
    "approved_at" TIMESTAMP(3),
    "notes" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "approval_requests_pkey" PRIMARY KEY ("id")
);

CREATE INDEX IF NOT EXISTS "approval_requests_company_id_entity_type_entity_id_idx"
  ON "approval_requests"("company_id", "entity_type", "entity_id");
CREATE INDEX IF NOT EXISTS "approval_requests_company_id_status_idx"
  ON "approval_requests"("company_id", "status");

ALTER TABLE "approval_requests" ADD CONSTRAINT "approval_requests_company_id_fkey"
  FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "journal_lines" ADD COLUMN IF NOT EXISTS "nominal_account_id" TEXT;

CREATE INDEX IF NOT EXISTS "journal_lines_nominal_account_id_idx"
  ON "journal_lines"("nominal_account_id");

ALTER TABLE "journal_lines" ADD CONSTRAINT "journal_lines_nominal_account_id_fkey"
  FOREIGN KEY ("nominal_account_id") REFERENCES "nominal_accounts"("id")
  ON DELETE SET NULL ON UPDATE CASCADE;
