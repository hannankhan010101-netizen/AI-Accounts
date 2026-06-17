-- Bank reconciliation timestamp on settlement documents (schema drift fix)

ALTER TABLE "bank_payments"
  ADD COLUMN IF NOT EXISTS "reconciled_at" TIMESTAMP(3);

ALTER TABLE "bank_receipts"
  ADD COLUMN IF NOT EXISTS "reconciled_at" TIMESTAMP(3);

ALTER TABLE "sales_receipts"
  ADD COLUMN IF NOT EXISTS "reconciled_at" TIMESTAMP(3);

ALTER TABLE "supplier_payments"
  ADD COLUMN IF NOT EXISTS "reconciled_at" TIMESTAMP(3);

ALTER TABLE "bank_transfers"
  ADD COLUMN IF NOT EXISTS "reconciled_at" TIMESTAMP(3);
