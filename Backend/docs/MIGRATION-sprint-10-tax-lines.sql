-- Sprint 10: tax fields on invoice/bill lines (run after setting DATABASE_URL)
-- prisma migrate dev --name sprint-10-tax-on-lines

ALTER TABLE sales_invoice_lines
  ADD COLUMN IF NOT EXISTS line_subtotal DECIMAL(18,4) NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS gst_code TEXT,
  ADD COLUMN IF NOT EXISTS gst_rate DECIMAL(8,4) NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS tax_amount DECIMAL(18,4) NOT NULL DEFAULT 0;

ALTER TABLE supplier_bill_lines
  ADD COLUMN IF NOT EXISTS line_subtotal DECIMAL(18,4) NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS gst_code TEXT,
  ADD COLUMN IF NOT EXISTS gst_rate DECIMAL(8,4) NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS tax_amount DECIMAL(18,4) NOT NULL DEFAULT 0;

-- Backfill subtotal from legacy rows where line_total was net-only
UPDATE sales_invoice_lines SET line_subtotal = line_total WHERE line_subtotal = 0;
UPDATE supplier_bill_lines SET line_subtotal = line_total WHERE line_subtotal = 0;
