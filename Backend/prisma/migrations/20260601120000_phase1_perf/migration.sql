-- Phase 1 API performance: indexes + outbox retry columns

-- Journal / GL hot paths
CREATE INDEX IF NOT EXISTS "idx_jl_nominal_journal"
  ON "journal_lines" ("nominal_code", "journal_id");

CREATE INDEX IF NOT EXISTS "idx_journals_company_status_date"
  ON "journals" ("company_id", "status", "journal_date");

-- Party-scoped commercial documents
CREATE INDEX IF NOT EXISTS "idx_sales_invoices_company_customer_date"
  ON "sales_invoices" ("company_id", "customer_id", "invoice_date");

CREATE INDEX IF NOT EXISTS "idx_supplier_bills_company_supplier_date"
  ON "supplier_bills" ("company_id", "supplier_id", "bill_date");

-- My Tasks draft/pending filters
CREATE INDEX IF NOT EXISTS "idx_sales_invoices_company_status_draft"
  ON "sales_invoices" ("company_id", "status")
  WHERE "status" IN ('draft', 'pending');

CREATE INDEX IF NOT EXISTS "idx_supplier_bills_company_status_draft"
  ON "supplier_bills" ("company_id", "status")
  WHERE "status" IN ('draft', 'pending');

-- Outbox worker poll
CREATE INDEX IF NOT EXISTS "idx_outbox_pending_created"
  ON "outbox_events" ("created_at")
  WHERE "status" = 'pending';

-- Outbox claim / retry
ALTER TABLE "outbox_events"
  ADD COLUMN IF NOT EXISTS "locked_at" TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS "next_attempt_at" TIMESTAMPTZ;
