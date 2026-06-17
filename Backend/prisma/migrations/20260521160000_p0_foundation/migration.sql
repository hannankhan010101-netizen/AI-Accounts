-- P0: journal traceability + stock adjustment GL link

ALTER TABLE "journals" ADD COLUMN IF NOT EXISTS "source_type" TEXT;
ALTER TABLE "journals" ADD COLUMN IF NOT EXISTS "source_id" TEXT;
ALTER TABLE "journals" ADD COLUMN IF NOT EXISTS "correlation_id" TEXT;
ALTER TABLE "journals" ADD COLUMN IF NOT EXISTS "reverses_journal_id" TEXT;

CREATE INDEX IF NOT EXISTS "journals_company_id_source_type_source_id_idx"
  ON "journals"("company_id", "source_type", "source_id");

ALTER TABLE "stock_adjustments" ADD COLUMN IF NOT EXISTS "journal_id" TEXT;
CREATE UNIQUE INDEX IF NOT EXISTS "stock_adjustments_journal_id_key" ON "stock_adjustments"("journal_id");

ALTER TABLE "stock_adjustments" ALTER COLUMN "status" SET DEFAULT 'draft';
