-- GST line fields on pre-GL planning documents (quotations, sales/purchase orders).

ALTER TABLE "quotation_lines" ADD COLUMN "line_subtotal" DECIMAL(18,4) NOT NULL DEFAULT 0;
ALTER TABLE "quotation_lines" ADD COLUMN "gst_code" TEXT;
ALTER TABLE "quotation_lines" ADD COLUMN "gst_rate" DECIMAL(8,4) NOT NULL DEFAULT 0;
ALTER TABLE "quotation_lines" ADD COLUMN "tax_amount" DECIMAL(18,4) NOT NULL DEFAULT 0;

UPDATE "quotation_lines"
SET "line_subtotal" = "quantity" * "rate"
WHERE "line_subtotal" = 0;

ALTER TABLE "sales_order_lines" ADD COLUMN "line_subtotal" DECIMAL(18,4) NOT NULL DEFAULT 0;
ALTER TABLE "sales_order_lines" ADD COLUMN "gst_code" TEXT;
ALTER TABLE "sales_order_lines" ADD COLUMN "gst_rate" DECIMAL(8,4) NOT NULL DEFAULT 0;
ALTER TABLE "sales_order_lines" ADD COLUMN "tax_amount" DECIMAL(18,4) NOT NULL DEFAULT 0;

UPDATE "sales_order_lines"
SET "line_subtotal" = "quantity" * "rate"
WHERE "line_subtotal" = 0;

ALTER TABLE "purchase_order_lines" ADD COLUMN "line_subtotal" DECIMAL(18,4) NOT NULL DEFAULT 0;
ALTER TABLE "purchase_order_lines" ADD COLUMN "gst_code" TEXT;
ALTER TABLE "purchase_order_lines" ADD COLUMN "gst_rate" DECIMAL(8,4) NOT NULL DEFAULT 0;
ALTER TABLE "purchase_order_lines" ADD COLUMN "tax_amount" DECIMAL(18,4) NOT NULL DEFAULT 0;

UPDATE "purchase_order_lines"
SET "line_subtotal" = "quantity" * "rate"
WHERE "line_subtotal" = 0;
