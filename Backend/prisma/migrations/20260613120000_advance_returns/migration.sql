-- Customer/supplier advance return tables (FA §5.8 / §6.4).
-- Required by AdvanceReturnService for unallocated balance on receipts/payments.

CREATE TABLE IF NOT EXISTS "customer_advance_returns" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "sales_receipt_id" TEXT NOT NULL,
    "bank_payment_id" TEXT NOT NULL,
    "amount" DECIMAL(18,4) NOT NULL,
    "return_date" TIMESTAMP(3) NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "customer_advance_returns_pkey" PRIMARY KEY ("id")
);

CREATE UNIQUE INDEX IF NOT EXISTS "customer_advance_returns_bank_payment_id_key"
  ON "customer_advance_returns"("bank_payment_id");

CREATE INDEX IF NOT EXISTS "customer_advance_returns_sales_receipt_id_idx"
  ON "customer_advance_returns"("sales_receipt_id");

CREATE TABLE IF NOT EXISTS "supplier_advance_returns" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "supplier_payment_id" TEXT NOT NULL,
    "bank_receipt_id" TEXT NOT NULL,
    "amount" DECIMAL(18,4) NOT NULL,
    "return_date" TIMESTAMP(3) NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "supplier_advance_returns_pkey" PRIMARY KEY ("id")
);

CREATE UNIQUE INDEX IF NOT EXISTS "supplier_advance_returns_bank_receipt_id_key"
  ON "supplier_advance_returns"("bank_receipt_id");

CREATE INDEX IF NOT EXISTS "supplier_advance_returns_supplier_payment_id_idx"
  ON "supplier_advance_returns"("supplier_payment_id");

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'customer_advance_returns_company_id_fkey'
  ) THEN
    ALTER TABLE "customer_advance_returns"
      ADD CONSTRAINT "customer_advance_returns_company_id_fkey"
      FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'customer_advance_returns_sales_receipt_id_fkey'
  ) THEN
    ALTER TABLE "customer_advance_returns"
      ADD CONSTRAINT "customer_advance_returns_sales_receipt_id_fkey"
      FOREIGN KEY ("sales_receipt_id") REFERENCES "sales_receipts"("id") ON DELETE CASCADE ON UPDATE CASCADE;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'customer_advance_returns_bank_payment_id_fkey'
  ) THEN
    ALTER TABLE "customer_advance_returns"
      ADD CONSTRAINT "customer_advance_returns_bank_payment_id_fkey"
      FOREIGN KEY ("bank_payment_id") REFERENCES "bank_payments"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'supplier_advance_returns_company_id_fkey'
  ) THEN
    ALTER TABLE "supplier_advance_returns"
      ADD CONSTRAINT "supplier_advance_returns_company_id_fkey"
      FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'supplier_advance_returns_supplier_payment_id_fkey'
  ) THEN
    ALTER TABLE "supplier_advance_returns"
      ADD CONSTRAINT "supplier_advance_returns_supplier_payment_id_fkey"
      FOREIGN KEY ("supplier_payment_id") REFERENCES "supplier_payments"("id") ON DELETE CASCADE ON UPDATE CASCADE;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'supplier_advance_returns_bank_receipt_id_fkey'
  ) THEN
    ALTER TABLE "supplier_advance_returns"
      ADD CONSTRAINT "supplier_advance_returns_bank_receipt_id_fkey"
      FOREIGN KEY ("bank_receipt_id") REFERENCES "bank_receipts"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
  END IF;
END $$;
