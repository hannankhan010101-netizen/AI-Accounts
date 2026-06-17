-- Step 1 CTE consolidation: composite indexes for hot read paths

CREATE INDEX IF NOT EXISTS "idx_sales_invoices_company_status_date"
  ON "sales_invoices" ("company_id", "status", "invoice_date");

CREATE INDEX IF NOT EXISTS "idx_sales_receipts_company_date"
  ON "sales_receipts" ("company_id", "receipt_date");

CREATE INDEX IF NOT EXISTS "idx_supplier_payments_company_date"
  ON "supplier_payments" ("company_id", "payment_date");

CREATE INDEX IF NOT EXISTS "idx_product_batches_company_code"
  ON "product_batches" ("company_id", "product_code");

CREATE INDEX IF NOT EXISTS "idx_grn_lines_product"
  ON "goods_receipt_note_lines" ("product_code");

CREATE INDEX IF NOT EXISTS "idx_supplier_bill_lines_product"
  ON "supplier_bill_lines" ("product_code");

CREATE INDEX IF NOT EXISTS "idx_bank_accounts_company_active"
  ON "bank_accounts" ("company_id", "is_active");
