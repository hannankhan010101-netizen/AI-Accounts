-- P2: goods issue, import payload, PDC workflow support

CREATE TABLE IF NOT EXISTS "goods_issues" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "voucher_number" TEXT NOT NULL,
    "issue_date" TIMESTAMP(3) NOT NULL,
    "sales_invoice_id" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'posted',
    "journal_id" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "goods_issues_pkey" PRIMARY KEY ("id")
);

CREATE UNIQUE INDEX IF NOT EXISTS "goods_issues_journal_id_key" ON "goods_issues"("journal_id");
CREATE UNIQUE INDEX IF NOT EXISTS "goods_issues_company_id_sales_invoice_id_key"
  ON "goods_issues"("company_id", "sales_invoice_id");
CREATE INDEX IF NOT EXISTS "goods_issues_company_id_issue_date_idx"
  ON "goods_issues"("company_id", "issue_date");

ALTER TABLE "goods_issues" ADD CONSTRAINT "goods_issues_company_id_fkey"
  FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

CREATE TABLE IF NOT EXISTS "goods_issue_lines" (
    "id" TEXT NOT NULL,
    "goods_issue_id" TEXT NOT NULL,
    "product_code" TEXT NOT NULL,
    "quantity" DECIMAL(18,4) NOT NULL,
    "unit_cost" DECIMAL(18,4) NOT NULL DEFAULT 0,
    CONSTRAINT "goods_issue_lines_pkey" PRIMARY KEY ("id")
);

CREATE INDEX IF NOT EXISTS "goods_issue_lines_goods_issue_id_idx"
  ON "goods_issue_lines"("goods_issue_id");

ALTER TABLE "goods_issue_lines" ADD CONSTRAINT "goods_issue_lines_goods_issue_id_fkey"
  FOREIGN KEY ("goods_issue_id") REFERENCES "goods_issues"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "import_jobs" ADD COLUMN IF NOT EXISTS "payload" JSONB NOT NULL DEFAULT '{}';
