-- P12: custom field validation columns, subscription billing stub

ALTER TABLE "custom_field_definitions"
  ADD COLUMN IF NOT EXISTS "is_required" BOOLEAN NOT NULL DEFAULT false,
  ADD COLUMN IF NOT EXISTS "picklist_options" JSONB;

CREATE TABLE IF NOT EXISTS "subscription_records" (
  "id" TEXT NOT NULL,
  "company_id" TEXT NOT NULL,
  "plan_code" TEXT NOT NULL DEFAULT 'standard',
  "external_customer_id" TEXT,
  "status" TEXT NOT NULL DEFAULT 'active',
  "current_period_end" TIMESTAMP(3),
  "metadata" JSONB NOT NULL DEFAULT '{}',
  "updated_at" TIMESTAMP(3) NOT NULL,
  CONSTRAINT "subscription_records_pkey" PRIMARY KEY ("id")
);

CREATE UNIQUE INDEX IF NOT EXISTS "subscription_records_company_id_key"
  ON "subscription_records"("company_id");

ALTER TABLE "subscription_records"
  ADD CONSTRAINT "subscription_records_company_id_fkey"
  FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;
