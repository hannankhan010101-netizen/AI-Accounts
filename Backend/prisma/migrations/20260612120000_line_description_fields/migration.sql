-- Line description + batch fields (schema parity with SalesInvoiceLine / SupplierBillLine)

ALTER TABLE "sales_invoice_lines" ADD COLUMN IF NOT EXISTS "description" TEXT;
ALTER TABLE "sales_invoice_lines" ADD COLUMN IF NOT EXISTS "description_fields" JSONB NOT NULL DEFAULT '{}';
ALTER TABLE "sales_invoice_lines" ADD COLUMN IF NOT EXISTS "batch_number" TEXT;
ALTER TABLE "sales_invoice_lines" ADD COLUMN IF NOT EXISTS "expiry_date" TIMESTAMP(3);

ALTER TABLE "supplier_bill_lines" ADD COLUMN IF NOT EXISTS "description" TEXT;
ALTER TABLE "supplier_bill_lines" ADD COLUMN IF NOT EXISTS "description_fields" JSONB NOT NULL DEFAULT '{}';
ALTER TABLE "supplier_bill_lines" ADD COLUMN IF NOT EXISTS "batch_number" TEXT;
ALTER TABLE "supplier_bill_lines" ADD COLUMN IF NOT EXISTS "expiry_date" TIMESTAMP(3);
