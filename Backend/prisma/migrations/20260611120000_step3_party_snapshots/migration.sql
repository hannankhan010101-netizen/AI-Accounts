-- Step 3: Party code/name snapshots on document headers (column locality)

-- Customer-side headers
ALTER TABLE "sales_invoices" ADD COLUMN IF NOT EXISTS "customer_code" TEXT;
ALTER TABLE "sales_invoices" ADD COLUMN IF NOT EXISTS "customer_name" TEXT;

ALTER TABLE "sales_receipts" ADD COLUMN IF NOT EXISTS "customer_code" TEXT;
ALTER TABLE "sales_receipts" ADD COLUMN IF NOT EXISTS "customer_name" TEXT;

ALTER TABLE "sales_credits" ADD COLUMN IF NOT EXISTS "customer_code" TEXT;
ALTER TABLE "sales_credits" ADD COLUMN IF NOT EXISTS "customer_name" TEXT;

ALTER TABLE "quotations" ADD COLUMN IF NOT EXISTS "customer_code" TEXT;
ALTER TABLE "quotations" ADD COLUMN IF NOT EXISTS "customer_name" TEXT;

ALTER TABLE "sales_orders" ADD COLUMN IF NOT EXISTS "customer_code" TEXT;
ALTER TABLE "sales_orders" ADD COLUMN IF NOT EXISTS "customer_name" TEXT;

ALTER TABLE "delivery_notes" ADD COLUMN IF NOT EXISTS "customer_code" TEXT;
ALTER TABLE "delivery_notes" ADD COLUMN IF NOT EXISTS "customer_name" TEXT;

ALTER TABLE "pdc_received" ADD COLUMN IF NOT EXISTS "customer_code" TEXT;
ALTER TABLE "pdc_received" ADD COLUMN IF NOT EXISTS "customer_name" TEXT;

-- Supplier-side headers
ALTER TABLE "supplier_bills" ADD COLUMN IF NOT EXISTS "supplier_code" TEXT;
ALTER TABLE "supplier_bills" ADD COLUMN IF NOT EXISTS "supplier_name" TEXT;

ALTER TABLE "supplier_payments" ADD COLUMN IF NOT EXISTS "supplier_code" TEXT;
ALTER TABLE "supplier_payments" ADD COLUMN IF NOT EXISTS "supplier_name" TEXT;

ALTER TABLE "supplier_credits" ADD COLUMN IF NOT EXISTS "supplier_code" TEXT;
ALTER TABLE "supplier_credits" ADD COLUMN IF NOT EXISTS "supplier_name" TEXT;

ALTER TABLE "purchase_orders" ADD COLUMN IF NOT EXISTS "supplier_code" TEXT;
ALTER TABLE "purchase_orders" ADD COLUMN IF NOT EXISTS "supplier_name" TEXT;

ALTER TABLE "goods_receipt_notes" ADD COLUMN IF NOT EXISTS "supplier_code" TEXT;
ALTER TABLE "goods_receipt_notes" ADD COLUMN IF NOT EXISTS "supplier_name" TEXT;

ALTER TABLE "pdc_issued" ADD COLUMN IF NOT EXISTS "supplier_code" TEXT;
ALTER TABLE "pdc_issued" ADD COLUMN IF NOT EXISTS "supplier_name" TEXT;

-- Backfill from masters
UPDATE "sales_invoices" si
SET "customer_code" = c."code", "customer_name" = c."name"
FROM "customers" c
WHERE c."id" = si."customer_id" AND si."customer_code" IS NULL;

UPDATE "sales_receipts" sr
SET "customer_code" = c."code", "customer_name" = c."name"
FROM "customers" c
WHERE c."id" = sr."customer_id" AND sr."customer_code" IS NULL;

UPDATE "sales_credits" sc
SET "customer_code" = c."code", "customer_name" = c."name"
FROM "customers" c
WHERE c."id" = sc."customer_id" AND sc."customer_code" IS NULL;

UPDATE "quotations" q
SET "customer_code" = c."code", "customer_name" = c."name"
FROM "customers" c
WHERE c."id" = q."customer_id" AND q."customer_code" IS NULL;

UPDATE "sales_orders" so
SET "customer_code" = c."code", "customer_name" = c."name"
FROM "customers" c
WHERE c."id" = so."customer_id" AND so."customer_code" IS NULL;

UPDATE "delivery_notes" dn
SET "customer_code" = c."code", "customer_name" = c."name"
FROM "customers" c
WHERE c."id" = dn."customer_id" AND dn."customer_code" IS NULL;

UPDATE "pdc_received" p
SET "customer_code" = c."code", "customer_name" = c."name"
FROM "customers" c
WHERE c."id" = p."customer_id" AND p."customer_code" IS NULL;

UPDATE "supplier_bills" sb
SET "supplier_code" = s."code", "supplier_name" = s."name"
FROM "suppliers" s
WHERE s."id" = sb."supplier_id" AND sb."supplier_code" IS NULL;

UPDATE "supplier_payments" sp
SET "supplier_code" = s."code", "supplier_name" = s."name"
FROM "suppliers" s
WHERE s."id" = sp."supplier_id" AND sp."supplier_code" IS NULL;

UPDATE "supplier_credits" sc
SET "supplier_code" = s."code", "supplier_name" = s."name"
FROM "suppliers" s
WHERE s."id" = sc."supplier_id" AND sc."supplier_code" IS NULL;

UPDATE "purchase_orders" po
SET "supplier_code" = s."code", "supplier_name" = s."name"
FROM "suppliers" s
WHERE s."id" = po."supplier_id" AND po."supplier_code" IS NULL;

UPDATE "goods_receipt_notes" grn
SET "supplier_code" = s."code", "supplier_name" = s."name"
FROM "suppliers" s
WHERE s."id" = grn."supplier_id" AND grn."supplier_code" IS NULL;

UPDATE "pdc_issued" p
SET "supplier_code" = s."code", "supplier_name" = s."name"
FROM "suppliers" s
WHERE s."id" = p."supplier_id" AND p."supplier_code" IS NULL;

-- Recreate AR/AP MVs with embedded party snapshots
DROP MATERIALIZED VIEW IF EXISTS "mv_ar_customer_open";
CREATE MATERIALIZED VIEW "mv_ar_customer_open" AS
SELECT
  si."company_id" AS company_id,
  si."customer_id" AS customer_id,
  MAX(si."customer_code") AS customer_code,
  MAX(si."customer_name") AS customer_name,
  SUM(si."remaining_amount") AS open_balance,
  MIN(si."invoice_date") FILTER (WHERE si."remaining_amount" > 0) AS oldest_open_date,
  COUNT(*) FILTER (WHERE si."remaining_amount" > 0)::int AS open_invoice_count
FROM "sales_invoices" si
WHERE si."status" = 'posted'
GROUP BY si."company_id", si."customer_id"
HAVING SUM(si."remaining_amount") > 0;

CREATE UNIQUE INDEX IF NOT EXISTS "mv_ar_customer_open_uidx"
  ON "mv_ar_customer_open" ("company_id", "customer_id");

DROP MATERIALIZED VIEW IF EXISTS "mv_ap_supplier_open";
CREATE MATERIALIZED VIEW "mv_ap_supplier_open" AS
SELECT
  sb."company_id" AS company_id,
  sb."supplier_id" AS supplier_id,
  MAX(sb."supplier_code") AS supplier_code,
  MAX(sb."supplier_name") AS supplier_name,
  SUM(sb."remaining_amount") AS open_balance,
  MIN(sb."bill_date") FILTER (WHERE sb."remaining_amount" > 0) AS oldest_open_date,
  COUNT(*) FILTER (WHERE sb."remaining_amount" > 0)::int AS open_bill_count
FROM "supplier_bills" sb
WHERE sb."status" = 'posted'
GROUP BY sb."company_id", sb."supplier_id"
HAVING SUM(sb."remaining_amount") > 0;

CREATE UNIQUE INDEX IF NOT EXISTS "mv_ap_supplier_open_uidx"
  ON "mv_ap_supplier_open" ("company_id", "supplier_id");
