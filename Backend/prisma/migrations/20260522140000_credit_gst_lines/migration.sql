-- GST line fields on sales and supplier credits.

ALTER TABLE "sales_credit_lines" ADD COLUMN "line_subtotal" DECIMAL(18,4) NOT NULL DEFAULT 0;
ALTER TABLE "sales_credit_lines" ADD COLUMN "gst_code" TEXT;
ALTER TABLE "sales_credit_lines" ADD COLUMN "gst_rate" DECIMAL(8,4) NOT NULL DEFAULT 0;
ALTER TABLE "sales_credit_lines" ADD COLUMN "tax_amount" DECIMAL(18,4) NOT NULL DEFAULT 0;

UPDATE "sales_credit_lines"
SET "line_subtotal" = "quantity" * "rate"
WHERE "line_subtotal" = 0;

ALTER TABLE "supplier_credit_lines" ADD COLUMN "line_subtotal" DECIMAL(18,4) NOT NULL DEFAULT 0;
ALTER TABLE "supplier_credit_lines" ADD COLUMN "gst_code" TEXT;
ALTER TABLE "supplier_credit_lines" ADD COLUMN "gst_rate" DECIMAL(8,4) NOT NULL DEFAULT 0;
ALTER TABLE "supplier_credit_lines" ADD COLUMN "tax_amount" DECIMAL(18,4) NOT NULL DEFAULT 0;

UPDATE "supplier_credit_lines"
SET "line_subtotal" = "quantity" * "rate"
WHERE "line_subtotal" = 0;
