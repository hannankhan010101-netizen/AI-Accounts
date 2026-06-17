-- P1: outbox, report runs, bank reconciliation, product cost

ALTER TABLE "products" ADD COLUMN IF NOT EXISTS "cost" DECIMAL(18,4) NOT NULL DEFAULT 0;

ALTER TABLE "import_jobs" ADD COLUMN IF NOT EXISTS "result_summary" TEXT;

CREATE TABLE IF NOT EXISTS "outbox_events" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "event_type" TEXT NOT NULL,
    "payload" JSONB NOT NULL DEFAULT '{}',
    "status" TEXT NOT NULL DEFAULT 'pending',
    "attempts" INTEGER NOT NULL DEFAULT 0,
    "last_error" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "processed_at" TIMESTAMP(3),
    CONSTRAINT "outbox_events_pkey" PRIMARY KEY ("id")
);

CREATE INDEX IF NOT EXISTS "outbox_events_company_id_status_created_at_idx"
  ON "outbox_events"("company_id", "status", "created_at");

ALTER TABLE "outbox_events" ADD CONSTRAINT "outbox_events_company_id_fkey"
  FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

CREATE TABLE IF NOT EXISTS "report_runs" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "report_id" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'pending',
    "criteria" JSONB NOT NULL DEFAULT '{}',
    "row_count" INTEGER NOT NULL DEFAULT 0,
    "rows" JSONB NOT NULL DEFAULT '[]',
    "error_message" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "completed_at" TIMESTAMP(3),
    CONSTRAINT "report_runs_pkey" PRIMARY KEY ("id")
);

CREATE INDEX IF NOT EXISTS "report_runs_company_id_report_id_created_at_idx"
  ON "report_runs"("company_id", "report_id", "created_at");

ALTER TABLE "report_runs" ADD CONSTRAINT "report_runs_company_id_fkey"
  FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

CREATE TABLE IF NOT EXISTS "bank_reconciliations" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "bank_account_id" TEXT NOT NULL,
    "statement_date" TIMESTAMP(3) NOT NULL,
    "statement_balance" DECIMAL(18,4) NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'open',
    "notes" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "completed_at" TIMESTAMP(3),
    CONSTRAINT "bank_reconciliations_pkey" PRIMARY KEY ("id")
);

CREATE INDEX IF NOT EXISTS "bank_reconciliations_company_id_bank_account_id_idx"
  ON "bank_reconciliations"("company_id", "bank_account_id");

ALTER TABLE "bank_reconciliations" ADD CONSTRAINT "bank_reconciliations_company_id_fkey"
  FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

CREATE TABLE IF NOT EXISTS "bank_reconciliation_items" (
    "id" TEXT NOT NULL,
    "reconciliation_id" TEXT NOT NULL,
    "item_type" TEXT NOT NULL,
    "item_id" TEXT NOT NULL,
    "transaction_date" TIMESTAMP(3) NOT NULL,
    "amount" DECIMAL(18,4) NOT NULL,
    "reference" TEXT,
    "is_cleared" BOOLEAN NOT NULL DEFAULT false,
    CONSTRAINT "bank_reconciliation_items_pkey" PRIMARY KEY ("id")
);

CREATE UNIQUE INDEX IF NOT EXISTS "bank_reconciliation_items_reconciliation_id_item_type_item_id_key"
  ON "bank_reconciliation_items"("reconciliation_id", "item_type", "item_id");

CREATE INDEX IF NOT EXISTS "bank_reconciliation_items_reconciliation_id_idx"
  ON "bank_reconciliation_items"("reconciliation_id");

ALTER TABLE "bank_reconciliation_items" ADD CONSTRAINT "bank_reconciliation_items_reconciliation_id_fkey"
  FOREIGN KEY ("reconciliation_id") REFERENCES "bank_reconciliations"("id") ON DELETE CASCADE ON UPDATE CASCADE;
