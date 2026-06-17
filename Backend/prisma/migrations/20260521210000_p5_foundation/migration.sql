-- P5: payment gateway transactions

CREATE TABLE IF NOT EXISTS "payment_gateway_transactions" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "provider" TEXT NOT NULL,
    "merchant_ref" TEXT NOT NULL,
    "amount" DECIMAL(18,4) NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'pending',
    "customer_id" TEXT,
    "sales_receipt_id" TEXT,
    "payload" JSONB NOT NULL DEFAULT '{}',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "payment_gateway_transactions_pkey" PRIMARY KEY ("id")
);

CREATE UNIQUE INDEX IF NOT EXISTS "payment_gateway_transactions_company_id_provider_merchant_ref_key"
  ON "payment_gateway_transactions"("company_id", "provider", "merchant_ref");
CREATE INDEX IF NOT EXISTS "payment_gateway_transactions_company_id_status_idx"
  ON "payment_gateway_transactions"("company_id", "status");

ALTER TABLE "payment_gateway_transactions" ADD CONSTRAINT "payment_gateway_transactions_company_id_fkey"
  FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;
