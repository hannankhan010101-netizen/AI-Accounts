-- P4: assembly, FX revaluation, FBR submissions

CREATE TABLE IF NOT EXISTS "assembly_templates" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "code" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "finished_product_code" TEXT NOT NULL,
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "assembly_templates_pkey" PRIMARY KEY ("id")
);
CREATE UNIQUE INDEX IF NOT EXISTS "assembly_templates_company_id_code_key"
  ON "assembly_templates"("company_id", "code");
ALTER TABLE "assembly_templates" ADD CONSTRAINT "assembly_templates_company_id_fkey"
  FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

CREATE TABLE IF NOT EXISTS "assembly_template_lines" (
    "id" TEXT NOT NULL,
    "template_id" TEXT NOT NULL,
    "component_product_code" TEXT NOT NULL,
    "quantity" DECIMAL(18,4) NOT NULL,
    CONSTRAINT "assembly_template_lines_pkey" PRIMARY KEY ("id")
);
CREATE INDEX IF NOT EXISTS "assembly_template_lines_template_id_idx"
  ON "assembly_template_lines"("template_id");
ALTER TABLE "assembly_template_lines" ADD CONSTRAINT "assembly_template_lines_template_id_fkey"
  FOREIGN KEY ("template_id") REFERENCES "assembly_templates"("id") ON DELETE CASCADE ON UPDATE CASCADE;

CREATE TABLE IF NOT EXISTS "assembly_jobs" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "job_number" TEXT NOT NULL,
    "job_date" TIMESTAMP(3) NOT NULL,
    "template_id" TEXT,
    "finished_product_code" TEXT NOT NULL,
    "quantity" DECIMAL(18,4) NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'draft',
    "journal_id" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "assembly_jobs_pkey" PRIMARY KEY ("id")
);
CREATE UNIQUE INDEX IF NOT EXISTS "assembly_jobs_journal_id_key" ON "assembly_jobs"("journal_id");
CREATE INDEX IF NOT EXISTS "assembly_jobs_company_id_job_date_idx"
  ON "assembly_jobs"("company_id", "job_date");
ALTER TABLE "assembly_jobs" ADD CONSTRAINT "assembly_jobs_company_id_fkey"
  FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "assembly_jobs" ADD CONSTRAINT "assembly_jobs_template_id_fkey"
  FOREIGN KEY ("template_id") REFERENCES "assembly_templates"("id") ON DELETE SET NULL ON UPDATE CASCADE;

CREATE TABLE IF NOT EXISTS "assembly_job_lines" (
    "id" TEXT NOT NULL,
    "job_id" TEXT NOT NULL,
    "component_product_code" TEXT NOT NULL,
    "quantity" DECIMAL(18,4) NOT NULL,
    "unit_cost" DECIMAL(18,4) NOT NULL DEFAULT 0,
    CONSTRAINT "assembly_job_lines_pkey" PRIMARY KEY ("id")
);
CREATE INDEX IF NOT EXISTS "assembly_job_lines_job_id_idx" ON "assembly_job_lines"("job_id");
ALTER TABLE "assembly_job_lines" ADD CONSTRAINT "assembly_job_lines_job_id_fkey"
  FOREIGN KEY ("job_id") REFERENCES "assembly_jobs"("id") ON DELETE CASCADE ON UPDATE CASCADE;

CREATE TABLE IF NOT EXISTS "fx_revaluation_runs" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "revaluation_date" TIMESTAMP(3) NOT NULL,
    "bank_account_id" TEXT NOT NULL,
    "foreign_balance" DECIMAL(18,4) NOT NULL,
    "exchange_rate" DECIMAL(18,8) NOT NULL,
    "gain_loss_amount" DECIMAL(18,4) NOT NULL,
    "journal_id" TEXT,
    "status" TEXT NOT NULL DEFAULT 'posted',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "fx_revaluation_runs_pkey" PRIMARY KEY ("id")
);
CREATE UNIQUE INDEX IF NOT EXISTS "fx_revaluation_runs_journal_id_key"
  ON "fx_revaluation_runs"("journal_id");
CREATE INDEX IF NOT EXISTS "fx_revaluation_runs_company_id_revaluation_date_idx"
  ON "fx_revaluation_runs"("company_id", "revaluation_date");
ALTER TABLE "fx_revaluation_runs" ADD CONSTRAINT "fx_revaluation_runs_company_id_fkey"
  FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

CREATE TABLE IF NOT EXISTS "digital_invoice_submissions" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "sales_invoice_id" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'pending',
    "fbr_reference" TEXT,
    "request_payload" JSONB NOT NULL DEFAULT '{}',
    "response_payload" JSONB,
    "submitted_at" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "digital_invoice_submissions_pkey" PRIMARY KEY ("id")
);
CREATE UNIQUE INDEX IF NOT EXISTS "digital_invoice_submissions_sales_invoice_id_key"
  ON "digital_invoice_submissions"("sales_invoice_id");
CREATE INDEX IF NOT EXISTS "digital_invoice_submissions_company_id_status_idx"
  ON "digital_invoice_submissions"("company_id", "status");
ALTER TABLE "digital_invoice_submissions" ADD CONSTRAINT "digital_invoice_submissions_company_id_fkey"
  FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;
