-- Saved transaction templates and recurring schedules (FA §3.3)

CREATE TABLE "transaction_templates" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "module" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "payload" JSONB NOT NULL DEFAULT '{}',
    "created_by" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "transaction_templates_pkey" PRIMARY KEY ("id")
);

CREATE INDEX "transaction_templates_company_id_module_idx"
    ON "transaction_templates"("company_id", "module");

ALTER TABLE "transaction_templates"
    ADD CONSTRAINT "transaction_templates_company_id_fkey"
    FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;

CREATE TABLE "recurring_schedules" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "module" TEXT NOT NULL,
    "frequency" TEXT NOT NULL DEFAULT 'monthly',
    "interval" INTEGER NOT NULL DEFAULT 1,
    "next_run_date" TIMESTAMP(3) NOT NULL,
    "end_date" TIMESTAMP(3),
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "payload" JSONB NOT NULL DEFAULT '{}',
    "last_run_at" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "recurring_schedules_pkey" PRIMARY KEY ("id")
);

CREATE INDEX "recurring_schedules_company_id_is_active_next_run_date_idx"
    ON "recurring_schedules"("company_id", "is_active", "next_run_date");

ALTER TABLE "recurring_schedules"
    ADD CONSTRAINT "recurring_schedules_company_id_fkey"
    FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;
