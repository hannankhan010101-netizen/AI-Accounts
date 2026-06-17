-- CreateEnum
CREATE TYPE "MigrationMode" AS ENUM ('batch', 'incremental', 'webhook', 'api_pull');

-- CreateEnum
CREATE TYPE "MigrationStatus" AS ENUM ('pending', 'extracting', 'validating', 'mapping', 'transforming', 'deduping', 'reconciling', 'importing', 'verifying', 'completed', 'failed', 'cancelled', 'rolling_back');

-- CreateEnum
CREATE TYPE "PipelineStage" AS ENUM ('extract', 'validate', 'map', 'transform', 'dedupe', 'reconcile', 'import', 'verify', 'audit');

-- CreateEnum
CREATE TYPE "ChunkStatus" AS ENUM ('pending', 'processing', 'completed', 'failed', 'skipped', 'rolled_back');

-- CreateEnum
CREATE TYPE "SourceType" AS ENUM ('csv', 'xlsx', 'json', 'api', 'webhook', 'fastaccounts');

-- CreateEnum
CREATE TYPE "EntityModule" AS ENUM ('customers', 'suppliers', 'chart_of_accounts', 'invoices', 'bills', 'receipts', 'payments', 'products', 'stock_movements', 'journals', 'taxes', 'projects', 'bank_transactions');

-- CreateEnum
CREATE TYPE "ValidationSeverity" AS ENUM ('error', 'warning', 'info');

-- CreateTable
CREATE TABLE "ing_migration_runs" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "module" "EntityModule" NOT NULL,
    "mode" "MigrationMode" NOT NULL DEFAULT 'batch',
    "status" "MigrationStatus" NOT NULL DEFAULT 'pending',
    "source_system" TEXT NOT NULL DEFAULT 'generic',
    "mapping_profile_id" TEXT,
    "source_type" "SourceType" NOT NULL,
    "source_key" TEXT,
    "source_file_name" TEXT,
    "total_rows" INTEGER NOT NULL DEFAULT 0,
    "processed_rows" INTEGER NOT NULL DEFAULT 0,
    "success_rows" INTEGER NOT NULL DEFAULT 0,
    "error_rows" INTEGER NOT NULL DEFAULT 0,
    "skipped_rows" INTEGER NOT NULL DEFAULT 0,
    "duplicate_rows" INTEGER NOT NULL DEFAULT 0,
    "chunk_size" INTEGER NOT NULL DEFAULT 500,
    "total_chunks" INTEGER NOT NULL DEFAULT 0,
    "completed_chunks" INTEGER NOT NULL DEFAULT 0,
    "current_stage" "PipelineStage",
    "options" JSONB NOT NULL DEFAULT '{}',
    "error_summary" TEXT,
    "started_at" TIMESTAMP(3),
    "completed_at" TIMESTAMP(3),
    "created_by_user_id" TEXT,
    "idempotency_key" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "ing_migration_runs_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ing_mapping_profiles" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "module" "EntityModule" NOT NULL,
    "source_system" TEXT NOT NULL DEFAULT 'generic',
    "is_default" BOOLEAN NOT NULL DEFAULT false,
    "description" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "ing_mapping_profiles_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ing_mapping_rules" (
    "id" TEXT NOT NULL,
    "mapping_profile_id" TEXT NOT NULL,
    "source_field" TEXT NOT NULL,
    "target_field" TEXT NOT NULL,
    "transform" TEXT,
    "default_value" TEXT,
    "is_required" BOOLEAN NOT NULL DEFAULT false,
    "confidence" DOUBLE PRECISION,
    "sort_order" INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT "ing_mapping_rules_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ing_staging_rows" (
    "id" TEXT NOT NULL,
    "migration_run_id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "row_index" INTEGER NOT NULL,
    "chunk_index" INTEGER NOT NULL,
    "source_data" JSONB NOT NULL,
    "mapped_data" JSONB,
    "transformed_data" JSONB,
    "fingerprint" TEXT,
    "external_id" TEXT,
    "is_duplicate" BOOLEAN NOT NULL DEFAULT false,
    "is_valid" BOOLEAN NOT NULL DEFAULT true,
    "imported" BOOLEAN NOT NULL DEFAULT false,
    "target_id" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "ing_staging_rows_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ing_migration_chunks" (
    "id" TEXT NOT NULL,
    "migration_run_id" TEXT NOT NULL,
    "chunk_index" INTEGER NOT NULL,
    "stage" "PipelineStage" NOT NULL,
    "status" "ChunkStatus" NOT NULL DEFAULT 'pending',
    "row_start" INTEGER NOT NULL,
    "row_end" INTEGER NOT NULL,
    "row_count" INTEGER NOT NULL DEFAULT 0,
    "success_count" INTEGER NOT NULL DEFAULT 0,
    "error_count" INTEGER NOT NULL DEFAULT 0,
    "attempts" INTEGER NOT NULL DEFAULT 0,
    "last_error" TEXT,
    "idempotency_key" TEXT NOT NULL,
    "started_at" TIMESTAMP(3),
    "completed_at" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "ing_migration_chunks_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ing_validation_issues" (
    "id" TEXT NOT NULL,
    "migration_run_id" TEXT NOT NULL,
    "row_index" INTEGER,
    "field" TEXT,
    "code" TEXT NOT NULL,
    "message" TEXT NOT NULL,
    "severity" "ValidationSeverity" NOT NULL DEFAULT 'error',
    "suggested_fix" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "ing_validation_issues_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ing_external_id_maps" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "migration_run_id" TEXT,
    "source_system" TEXT NOT NULL,
    "entity_module" "EntityModule" NOT NULL,
    "external_id" TEXT NOT NULL,
    "target_id" TEXT NOT NULL,
    "target_code" TEXT,
    "metadata" JSONB NOT NULL DEFAULT '{}',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "ing_external_id_maps_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ing_stage_logs" (
    "id" TEXT NOT NULL,
    "migration_run_id" TEXT NOT NULL,
    "stage" "PipelineStage" NOT NULL,
    "chunk_index" INTEGER,
    "status" TEXT NOT NULL,
    "message" TEXT,
    "metrics" JSONB NOT NULL DEFAULT '{}',
    "duration_ms" INTEGER,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "ing_stage_logs_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ing_reconciliation_reports" (
    "id" TEXT NOT NULL,
    "migration_run_id" TEXT NOT NULL,
    "passed" BOOLEAN NOT NULL DEFAULT false,
    "gl_balanced" BOOLEAN,
    "gl_delta" TEXT,
    "inventory_delta" TEXT,
    "ar_total" TEXT,
    "ap_total" TEXT,
    "details" JSONB NOT NULL DEFAULT '{}',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "ing_reconciliation_reports_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ing_audit_entries" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "migration_run_id" TEXT,
    "action" TEXT NOT NULL,
    "actor_user_id" TEXT,
    "entity_type" TEXT,
    "entity_id" TEXT,
    "details" JSONB NOT NULL DEFAULT '{}',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "ing_audit_entries_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ing_webhook_subscriptions" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "provider" TEXT NOT NULL,
    "secret_hash" TEXT NOT NULL,
    "module" "EntityModule" NOT NULL,
    "mapping_profile_id" TEXT,
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "ing_webhook_subscriptions_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "ing_migration_runs_idempotency_key_key" ON "ing_migration_runs"("idempotency_key");

-- CreateIndex
CREATE INDEX "ing_migration_runs_company_id_status_idx" ON "ing_migration_runs"("company_id", "status");

-- CreateIndex
CREATE INDEX "ing_migration_runs_company_id_module_idx" ON "ing_migration_runs"("company_id", "module");

-- CreateIndex
CREATE UNIQUE INDEX "ing_mapping_profiles_company_id_name_key" ON "ing_mapping_profiles"("company_id", "name");

-- CreateIndex
CREATE INDEX "ing_mapping_profiles_company_id_module_idx" ON "ing_mapping_profiles"("company_id", "module");

-- CreateIndex
CREATE UNIQUE INDEX "ing_mapping_rules_mapping_profile_id_target_field_key" ON "ing_mapping_rules"("mapping_profile_id", "target_field");

-- CreateIndex
CREATE UNIQUE INDEX "ing_staging_rows_migration_run_id_row_index_key" ON "ing_staging_rows"("migration_run_id", "row_index");

-- CreateIndex
CREATE INDEX "ing_staging_rows_migration_run_id_chunk_index_idx" ON "ing_staging_rows"("migration_run_id", "chunk_index");

-- CreateIndex
CREATE INDEX "ing_staging_rows_migration_run_id_fingerprint_idx" ON "ing_staging_rows"("migration_run_id", "fingerprint");

-- CreateIndex
CREATE INDEX "ing_staging_rows_company_id_external_id_idx" ON "ing_staging_rows"("company_id", "external_id");

-- CreateIndex
CREATE UNIQUE INDEX "ing_migration_chunks_idempotency_key_key" ON "ing_migration_chunks"("idempotency_key");

-- CreateIndex
CREATE UNIQUE INDEX "ing_migration_chunks_migration_run_id_chunk_index_stage_key" ON "ing_migration_chunks"("migration_run_id", "chunk_index", "stage");

-- CreateIndex
CREATE INDEX "ing_migration_chunks_migration_run_id_status_idx" ON "ing_migration_chunks"("migration_run_id", "status");

-- CreateIndex
CREATE INDEX "ing_validation_issues_migration_run_id_severity_idx" ON "ing_validation_issues"("migration_run_id", "severity");

-- CreateIndex
CREATE UNIQUE INDEX "ing_external_id_maps_company_id_source_system_entity_module_ex_key" ON "ing_external_id_maps"("company_id", "source_system", "entity_module", "external_id");

-- CreateIndex
CREATE INDEX "ing_external_id_maps_company_id_entity_module_target_id_idx" ON "ing_external_id_maps"("company_id", "entity_module", "target_id");

-- CreateIndex
CREATE INDEX "ing_stage_logs_migration_run_id_stage_idx" ON "ing_stage_logs"("migration_run_id", "stage");

-- CreateIndex
CREATE UNIQUE INDEX "ing_reconciliation_reports_migration_run_id_key" ON "ing_reconciliation_reports"("migration_run_id");

-- CreateIndex
CREATE INDEX "ing_audit_entries_company_id_created_at_idx" ON "ing_audit_entries"("company_id", "created_at");

-- CreateIndex
CREATE INDEX "ing_audit_entries_migration_run_id_idx" ON "ing_audit_entries"("migration_run_id");

-- CreateIndex
CREATE UNIQUE INDEX "ing_webhook_subscriptions_company_id_provider_module_key" ON "ing_webhook_subscriptions"("company_id", "provider", "module");

-- AddForeignKey
ALTER TABLE "ing_migration_runs" ADD CONSTRAINT "ing_migration_runs_mapping_profile_id_fkey" FOREIGN KEY ("mapping_profile_id") REFERENCES "ing_mapping_profiles"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ing_mapping_rules" ADD CONSTRAINT "ing_mapping_rules_mapping_profile_id_fkey" FOREIGN KEY ("mapping_profile_id") REFERENCES "ing_mapping_profiles"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ing_staging_rows" ADD CONSTRAINT "ing_staging_rows_migration_run_id_fkey" FOREIGN KEY ("migration_run_id") REFERENCES "ing_migration_runs"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ing_migration_chunks" ADD CONSTRAINT "ing_migration_chunks_migration_run_id_fkey" FOREIGN KEY ("migration_run_id") REFERENCES "ing_migration_runs"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ing_validation_issues" ADD CONSTRAINT "ing_validation_issues_migration_run_id_fkey" FOREIGN KEY ("migration_run_id") REFERENCES "ing_migration_runs"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ing_external_id_maps" ADD CONSTRAINT "ing_external_id_maps_migration_run_id_fkey" FOREIGN KEY ("migration_run_id") REFERENCES "ing_migration_runs"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ing_stage_logs" ADD CONSTRAINT "ing_stage_logs_migration_run_id_fkey" FOREIGN KEY ("migration_run_id") REFERENCES "ing_migration_runs"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ing_reconciliation_reports" ADD CONSTRAINT "ing_reconciliation_reports_migration_run_id_fkey" FOREIGN KEY ("migration_run_id") REFERENCES "ing_migration_runs"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ing_audit_entries" ADD CONSTRAINT "ing_audit_entries_migration_run_id_fkey" FOREIGN KEY ("migration_run_id") REFERENCES "ing_migration_runs"("id") ON DELETE SET NULL ON UPDATE CASCADE;
