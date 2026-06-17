-- Phase 5: assistant thread listing + report line aggregates support

CREATE INDEX IF NOT EXISTS "assistant_threads_company_user_updated_idx"
  ON "assistant_threads" ("company_id", "user_id", "updated_at" DESC);

CREATE INDEX IF NOT EXISTS "sales_invoice_lines_product_invoice_idx"
  ON "sales_invoice_lines" ("sales_invoice_id", "product_code");

CREATE INDEX IF NOT EXISTS "supplier_bill_lines_product_bill_idx"
  ON "supplier_bill_lines" ("supplier_bill_id", "product_code");
