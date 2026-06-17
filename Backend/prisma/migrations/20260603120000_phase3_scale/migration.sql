-- Phase 3: denormalized open balances, materialized views, archival indexes

-- Open balance on AR/AP documents (maintained on allocation changes)
ALTER TABLE "sales_invoices"
  ADD COLUMN IF NOT EXISTS "remaining_amount" DECIMAL(18, 4);

ALTER TABLE "supplier_bills"
  ADD COLUMN IF NOT EXISTS "remaining_amount" DECIMAL(18, 4);

UPDATE "sales_invoices" si
SET "remaining_amount" = GREATEST(
  0,
  si."total_amount" - COALESCE(
    (SELECT SUM(a."amount") FROM "sales_receipt_allocations" a WHERE a."sales_invoice_id" = si."id"),
    0
  )
)
WHERE "remaining_amount" IS NULL;

UPDATE "supplier_bills" sb
SET "remaining_amount" = GREATEST(
  0,
  sb."total_amount" - COALESCE(
    (SELECT SUM(a."amount") FROM "supplier_payment_allocations" a WHERE a."supplier_bill_id" = sb."id"),
    0
  )
)
WHERE "remaining_amount" IS NULL;

ALTER TABLE "sales_invoices"
  ALTER COLUMN "remaining_amount" SET DEFAULT 0;

ALTER TABLE "supplier_bills"
  ALTER COLUMN "remaining_amount" SET DEFAULT 0;

CREATE INDEX IF NOT EXISTS "idx_sales_invoices_open_remaining"
  ON "sales_invoices" ("company_id", "customer_id", "invoice_date")
  WHERE "remaining_amount" > 0;

CREATE INDEX IF NOT EXISTS "idx_supplier_bills_open_remaining"
  ON "supplier_bills" ("company_id", "supplier_id", "bill_date")
  WHERE "remaining_amount" > 0;

-- Trial balance snapshot (all posted journals; refresh after posting)
DROP MATERIALIZED VIEW IF EXISTS "mv_nominal_balances";
CREATE MATERIALIZED VIEW "mv_nominal_balances" AS
SELECT
  j."company_id" AS company_id,
  jl."nominal_code" AS nominal_code,
  SUM(jl."debit") AS debit,
  SUM(jl."credit") AS credit,
  SUM(jl."debit" - jl."credit") AS balance
FROM "journal_lines" jl
INNER JOIN "journals" j ON j."id" = jl."journal_id"
WHERE j."status" = 'posted'
GROUP BY j."company_id", jl."nominal_code";

CREATE UNIQUE INDEX IF NOT EXISTS "mv_nominal_balances_company_nominal_uidx"
  ON "mv_nominal_balances" ("company_id", "nominal_code");

-- AR open balances per customer (for aging)
DROP MATERIALIZED VIEW IF EXISTS "mv_ar_customer_open";
CREATE MATERIALIZED VIEW "mv_ar_customer_open" AS
SELECT
  si."company_id" AS company_id,
  si."customer_id" AS customer_id,
  SUM(si."remaining_amount") AS open_balance,
  MIN(si."invoice_date") FILTER (WHERE si."remaining_amount" > 0) AS oldest_open_date,
  COUNT(*) FILTER (WHERE si."remaining_amount" > 0)::int AS open_invoice_count
FROM "sales_invoices" si
WHERE si."status" = 'posted'
GROUP BY si."company_id", si."customer_id"
HAVING SUM(si."remaining_amount") > 0;

CREATE UNIQUE INDEX IF NOT EXISTS "mv_ar_customer_open_uidx"
  ON "mv_ar_customer_open" ("company_id", "customer_id");

-- AP open balances per supplier
DROP MATERIALIZED VIEW IF EXISTS "mv_ap_supplier_open";
CREATE MATERIALIZED VIEW "mv_ap_supplier_open" AS
SELECT
  sb."company_id" AS company_id,
  sb."supplier_id" AS supplier_id,
  SUM(sb."remaining_amount") AS open_balance,
  MIN(sb."bill_date") FILTER (WHERE sb."remaining_amount" > 0) AS oldest_open_date,
  COUNT(*) FILTER (WHERE sb."remaining_amount" > 0)::int AS open_bill_count
FROM "supplier_bills" sb
WHERE sb."status" = 'posted'
GROUP BY sb."company_id", sb."supplier_id"
HAVING SUM(sb."remaining_amount") > 0;

CREATE UNIQUE INDEX IF NOT EXISTS "mv_ap_supplier_open_uidx"
  ON "mv_ap_supplier_open" ("company_id", "supplier_id");

-- Archival / maintenance indexes
CREATE INDEX IF NOT EXISTS "idx_outbox_completed_processed"
  ON "outbox_events" ("processed_at")
  WHERE "status" = 'completed';

CREATE INDEX IF NOT EXISTS "idx_audit_log_created"
  ON "audit_log_entries" ("created_at");
