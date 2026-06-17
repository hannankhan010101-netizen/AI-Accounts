-- Step 2: Search speed — composite B-tree + pg_trgm GIN indexes
--
-- Redundant with Step 1 (keep both; planner picks best):
--   idx_sales_invoices_company_status_date — superseded by idx_step2_si_keyset (+ id tie-breaker)
--   idx_sales_receipts_company_date — superseded by idx_step2_sr_customer_date
--   idx_supplier_payments_company_date — superseded by idx_step2_sp_supplier_date
--
-- Schema @@index blocks mirror btree composites; GIN/trgm indexes are migration-only.

CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- =================== P0 — keyset pagination & report lists ===================

CREATE INDEX IF NOT EXISTS "idx_step2_si_keyset"
  ON "sales_invoices" ("company_id", "status", "invoice_date" DESC, "id" DESC);

CREATE INDEX IF NOT EXISTS "idx_step2_sb_keyset"
  ON "supplier_bills" ("company_id", "status", "bill_date" DESC, "id" DESC);

CREATE INDEX IF NOT EXISTS "idx_step2_bank_payments_keyset"
  ON "bank_payments" ("company_id", "payment_date" DESC, "id" DESC);

CREATE INDEX IF NOT EXISTS "idx_step2_bank_receipts_keyset"
  ON "bank_receipts" ("company_id", "receipt_date" DESC, "id" DESC);

CREATE INDEX IF NOT EXISTS "idx_step2_bank_transfers_keyset"
  ON "bank_transfers" ("company_id", "transfer_date" DESC, "id" DESC);

CREATE INDEX IF NOT EXISTS "idx_step2_stock_adjustments_keyset"
  ON "stock_adjustments" ("company_id", "adjustment_date" DESC, "id" DESC);

CREATE INDEX IF NOT EXISTS "idx_step2_stock_transfers_keyset"
  ON "stock_transfers" ("company_id", "transfer_date" DESC, "id" DESC);

CREATE INDEX IF NOT EXISTS "idx_step2_assembly_jobs_keyset"
  ON "assembly_jobs" ("company_id", "job_date" DESC, "id" DESC);

CREATE INDEX IF NOT EXISTS "idx_step2_products_active_code"
  ON "products" ("company_id", "code" ASC, "id" ASC)
  WHERE "is_archived" = false;

CREATE INDEX IF NOT EXISTS "idx_step2_customers_code"
  ON "customers" ("company_id", "code" ASC, "id" ASC);

CREATE INDEX IF NOT EXISTS "idx_step2_suppliers_code"
  ON "suppliers" ("company_id", "code" ASC, "id" ASC);

-- =================== P1 — subledger, activity feeds ===================

CREATE INDEX IF NOT EXISTS "idx_step2_sr_customer_date"
  ON "sales_receipts" ("company_id", "customer_id", "receipt_date" DESC);

CREATE INDEX IF NOT EXISTS "idx_step2_sp_supplier_date"
  ON "supplier_payments" ("company_id", "supplier_id", "payment_date" DESC);

CREATE INDEX IF NOT EXISTS "idx_step2_si_customer_status_date"
  ON "sales_invoices" ("company_id", "customer_id", "status", "invoice_date" DESC);

CREATE INDEX IF NOT EXISTS "idx_step2_sb_supplier_status_date"
  ON "supplier_bills" ("company_id", "supplier_id", "status", "bill_date" DESC);

CREATE INDEX IF NOT EXISTS "idx_step2_sales_credits_customer_date"
  ON "sales_credits" ("company_id", "customer_id", "credit_date" DESC);

CREATE INDEX IF NOT EXISTS "idx_step2_supplier_credits_supplier_date"
  ON "supplier_credits" ("company_id", "supplier_id", "credit_date" DESC);

CREATE INDEX IF NOT EXISTS "idx_step2_quotations_customer_date"
  ON "quotations" ("company_id", "customer_id", "quotation_date" DESC);

CREATE INDEX IF NOT EXISTS "idx_step2_sales_orders_customer_date"
  ON "sales_orders" ("company_id", "customer_id", "order_date" DESC);

CREATE INDEX IF NOT EXISTS "idx_step2_purchase_orders_supplier_date"
  ON "purchase_orders" ("company_id", "supplier_id", "order_date" DESC);

CREATE INDEX IF NOT EXISTS "idx_step2_delivery_notes_customer_date"
  ON "delivery_notes" ("company_id", "customer_id", "delivery_date" DESC);

CREATE INDEX IF NOT EXISTS "idx_step2_grn_supplier_date"
  ON "goods_receipt_notes" ("company_id", "supplier_id", "receipt_date" DESC);

CREATE INDEX IF NOT EXISTS "idx_step2_pdc_received_customer_date"
  ON "pdc_received" ("company_id", "customer_id", "received_date" DESC);

CREATE INDEX IF NOT EXISTS "idx_step2_pdc_issued_supplier_date"
  ON "pdc_issued" ("company_id", "supplier_id", "issued_date" DESC);

-- =================== P1 — My Tasks partial draft indexes ===================

CREATE INDEX IF NOT EXISTS "idx_step2_sales_credits_draft"
  ON "sales_credits" ("company_id", "credit_date" DESC)
  WHERE "status" = 'draft';

CREATE INDEX IF NOT EXISTS "idx_step2_supplier_credits_draft"
  ON "supplier_credits" ("company_id", "credit_date" DESC)
  WHERE "status" = 'draft';

CREATE INDEX IF NOT EXISTS "idx_step2_quotations_draft"
  ON "quotations" ("company_id", "quotation_date" DESC)
  WHERE "status" = 'draft';

CREATE INDEX IF NOT EXISTS "idx_step2_sales_orders_draft"
  ON "sales_orders" ("company_id", "order_date" DESC)
  WHERE "status" = 'draft';

CREATE INDEX IF NOT EXISTS "idx_step2_purchase_orders_draft"
  ON "purchase_orders" ("company_id", "order_date" DESC)
  WHERE "status" = 'draft';

CREATE INDEX IF NOT EXISTS "idx_step2_journals_draft"
  ON "journals" ("company_id", "journal_date" DESC)
  WHERE "status" = 'draft';

-- =================== P1 — audit log btree filters ===================

CREATE INDEX IF NOT EXISTS "idx_step2_audit_company_user_created"
  ON "audit_log_entries" ("company_id", "user_id", "created_at" DESC);

CREATE INDEX IF NOT EXISTS "idx_step2_audit_company_transaction_id"
  ON "audit_log_entries" ("company_id", "transaction_id");

CREATE INDEX IF NOT EXISTS "idx_step2_audit_company_type_created"
  ON "audit_log_entries" ("company_id", "transaction_type", "created_at" DESC);

-- =================== P1 — pg_trgm text search (GIN) ===================

CREATE INDEX IF NOT EXISTS "idx_step2_audit_transaction_type_trgm"
  ON "audit_log_entries" USING gin ("transaction_type" gin_trgm_ops);

CREATE INDEX IF NOT EXISTS "idx_step2_users_email_trgm"
  ON "User" USING gin ("email" gin_trgm_ops);

CREATE INDEX IF NOT EXISTS "idx_step2_users_first_name_trgm"
  ON "User" USING gin ("first_name" gin_trgm_ops);

CREATE INDEX IF NOT EXISTS "idx_step2_users_last_name_trgm"
  ON "User" USING gin ("last_name" gin_trgm_ops);

CREATE INDEX IF NOT EXISTS "idx_step2_memberships_company_role"
  ON "company_memberships" ("company_id", "role_id");

-- =================== P2 — workers & secondary paths ===================

CREATE INDEX IF NOT EXISTS "idx_step2_outbox_pending_claim"
  ON "outbox_events" ("status", "next_attempt_at", "created_at" ASC)
  WHERE "status" = 'pending';

CREATE INDEX IF NOT EXISTS "idx_step2_report_runs_completed"
  ON "report_runs" ("company_id", "status", "completed_at" DESC);

CREATE INDEX IF NOT EXISTS "idx_step2_approval_requests_queue"
  ON "approval_requests" ("company_id", "status", "created_at" DESC);

CREATE INDEX IF NOT EXISTS "idx_step2_journal_lines_project"
  ON "journal_lines" ("project_code")
  WHERE "project_code" IS NOT NULL;

CREATE INDEX IF NOT EXISTS "idx_step2_grn_lines_note_product"
  ON "goods_receipt_note_lines" ("goods_receipt_note_id", "product_code");
