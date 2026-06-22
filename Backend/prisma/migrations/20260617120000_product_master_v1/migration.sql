-- Product master v1: image pointer, stock hints, updated_at, search indexes

ALTER TABLE "products" ADD COLUMN IF NOT EXISTS "primary_image_attachment_id" TEXT;
ALTER TABLE "products" ADD COLUMN IF NOT EXISTS "low_stock_level" DECIMAL(18,4);
ALTER TABLE "products" ADD COLUMN IF NOT EXISTS "bin_location" TEXT;
ALTER TABLE "products" ADD COLUMN IF NOT EXISTS "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP;

CREATE INDEX IF NOT EXISTS "products_company_id_is_archived_idx" ON "products"("company_id", "is_archived");
CREATE INDEX IF NOT EXISTS "products_company_id_name_idx" ON "products"("company_id", "name");
CREATE INDEX IF NOT EXISTS "products_company_id_category_idx" ON "products"("company_id", "category");
