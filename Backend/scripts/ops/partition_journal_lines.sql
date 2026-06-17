-- Phase 4 runbook: journal_lines range partitioning (ops-only, not auto-applied)
-- Run during a maintenance window on self-hosted Postgres with sufficient privileges.
-- Supabase managed Postgres may require support / project upgrade for declarative partitioning.

-- 1) Rename existing table
-- ALTER TABLE journal_lines RENAME TO journal_lines_legacy;

-- 2) Create partitioned parent (example: monthly on journal created_at via join)
-- CREATE TABLE journal_lines (
--   LIKE journal_lines_legacy INCLUDING ALL
-- ) PARTITION BY RANGE (journal_id);
-- Note: Prisma expects a single journal_lines table — coordinate ORM + migration carefully.

-- 3) Create partitions per month and migrate data in batches
-- CREATE TABLE journal_lines_2026_01 PARTITION OF journal_lines
--   FOR VALUES FROM ('min_id_jan') TO ('min_id_feb');

-- 4) Rebuild indexes on each partition; ANALYZE journal_lines;

-- Until partitioning is applied, rely on:
--   - mv_nominal_balances (Phase 3)
--   - idx_jl_nominal_journal, idx_journals_company_status_date (Phase 1)
