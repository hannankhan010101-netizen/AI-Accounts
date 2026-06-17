-- Smart filter / document metadata JSON on transactional headers (schema drift fix)

ALTER TABLE "sales_invoices"
  ADD COLUMN IF NOT EXISTS "custom_fields" JSONB NOT NULL DEFAULT '{}';

ALTER TABLE "supplier_bills"
  ADD COLUMN IF NOT EXISTS "custom_fields" JSONB NOT NULL DEFAULT '{}';

ALTER TABLE "sales_receipts"
  ADD COLUMN IF NOT EXISTS "custom_fields" JSONB NOT NULL DEFAULT '{}';

ALTER TABLE "supplier_payments"
  ADD COLUMN IF NOT EXISTS "custom_fields" JSONB NOT NULL DEFAULT '{}';

ALTER TABLE "bank_payments"
  ADD COLUMN IF NOT EXISTS "custom_fields" JSONB NOT NULL DEFAULT '{}';

ALTER TABLE "bank_receipts"
  ADD COLUMN IF NOT EXISTS "custom_fields" JSONB NOT NULL DEFAULT '{}';
