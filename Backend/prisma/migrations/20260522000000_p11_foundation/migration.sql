-- P11: custom fields, product UOM, module entitlements, product pricing columns

ALTER TABLE "customers"
  ADD COLUMN IF NOT EXISTS "custom_fields" JSONB NOT NULL DEFAULT '{}';

ALTER TABLE "products"
  ADD COLUMN IF NOT EXISTS "category" TEXT,
  ADD COLUMN IF NOT EXISTS "unit" TEXT NOT NULL DEFAULT 'EA',
  ADD COLUMN IF NOT EXISTS "sale_price" DECIMAL(18,4) NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS "custom_fields" JSONB NOT NULL DEFAULT '{}';

CREATE TABLE IF NOT EXISTS "company_module_entitlements" (
  "id" TEXT NOT NULL,
  "company_id" TEXT NOT NULL,
  "module_code" TEXT NOT NULL,
  "enabled" BOOLEAN NOT NULL DEFAULT true,
  "updated_at" TIMESTAMP(3) NOT NULL,
  CONSTRAINT "company_module_entitlements_pkey" PRIMARY KEY ("id")
);

CREATE UNIQUE INDEX IF NOT EXISTS "company_module_entitlements_company_id_module_code_key"
  ON "company_module_entitlements"("company_id", "module_code");
CREATE INDEX IF NOT EXISTS "company_module_entitlements_company_id_idx"
  ON "company_module_entitlements"("company_id");

ALTER TABLE "company_module_entitlements"
  ADD CONSTRAINT "company_module_entitlements_company_id_fkey"
  FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

CREATE TABLE IF NOT EXISTS "custom_field_definitions" (
  "id" TEXT NOT NULL,
  "company_id" TEXT NOT NULL,
  "entity_type" TEXT NOT NULL,
  "field_key" TEXT NOT NULL,
  "label" TEXT NOT NULL,
  "field_type" TEXT NOT NULL DEFAULT 'text',
  "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "custom_field_definitions_pkey" PRIMARY KEY ("id")
);

CREATE UNIQUE INDEX IF NOT EXISTS "custom_field_definitions_company_id_entity_type_field_key_key"
  ON "custom_field_definitions"("company_id", "entity_type", "field_key");
CREATE INDEX IF NOT EXISTS "custom_field_definitions_company_id_entity_type_idx"
  ON "custom_field_definitions"("company_id", "entity_type");

ALTER TABLE "custom_field_definitions"
  ADD CONSTRAINT "custom_field_definitions_company_id_fkey"
  FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

CREATE TABLE IF NOT EXISTS "product_uoms" (
  "id" TEXT NOT NULL,
  "company_id" TEXT NOT NULL,
  "product_id" TEXT NOT NULL,
  "unit_code" TEXT NOT NULL,
  "conversion_factor" DECIMAL(18,6) NOT NULL DEFAULT 1,
  "sale_price" DECIMAL(18,4) NOT NULL DEFAULT 0,
  "is_default" BOOLEAN NOT NULL DEFAULT false,
  CONSTRAINT "product_uoms_pkey" PRIMARY KEY ("id")
);

CREATE UNIQUE INDEX IF NOT EXISTS "product_uoms_company_id_product_id_unit_code_key"
  ON "product_uoms"("company_id", "product_id", "unit_code");
CREATE INDEX IF NOT EXISTS "product_uoms_product_id_idx" ON "product_uoms"("product_id");

ALTER TABLE "product_uoms"
  ADD CONSTRAINT "product_uoms_product_id_fkey"
  FOREIGN KEY ("product_id") REFERENCES "products"("id") ON DELETE CASCADE ON UPDATE CASCADE;
