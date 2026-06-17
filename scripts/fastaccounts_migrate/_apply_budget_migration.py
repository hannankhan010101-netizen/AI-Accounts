#!/usr/bin/env python3
"""Fix budget migration FK to Company table (Prisma uses \"Company\", not companies)."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "Backend"
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

import os

if os.getenv("DIRECT_URL"):
    os.environ["DATABASE_URL"] = os.environ["DIRECT_URL"]

from prisma_generated import Prisma


async def main() -> None:
    db = Prisma()
    await db.connect()

    tables = await db.query_raw(
        """
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name IN ('budgets', 'budget_lines')
        ORDER BY 1
        """
    )
    names = {r["table_name"] for r in tables}
    print(f"tables present: {sorted(names)}")

    if "budgets" not in names:
        await db.execute_raw(
            """
            CREATE TABLE "budgets" (
                "id" TEXT NOT NULL,
                "company_id" TEXT NOT NULL,
                "code" TEXT NOT NULL,
                "name" TEXT NOT NULL,
                "fiscal_year" INTEGER NOT NULL,
                "is_active" BOOLEAN NOT NULL DEFAULT true,
                "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT "budgets_pkey" PRIMARY KEY ("id")
            )
            """
        )
        print("created budgets")

    if "budget_lines" not in names:
        await db.execute_raw(
            """
            CREATE TABLE "budget_lines" (
                "id" TEXT NOT NULL,
                "budget_id" TEXT NOT NULL,
                "nominal_code" TEXT NOT NULL,
                "period" TEXT NOT NULL DEFAULT 'annual',
                "amount" DECIMAL(18,4) NOT NULL,
                CONSTRAINT "budget_lines_pkey" PRIMARY KEY ("id")
            )
            """
        )
        print("created budget_lines")

    indexes = await db.query_raw(
        """
        SELECT indexname FROM pg_indexes
        WHERE schemaname = 'public' AND tablename = 'budgets'
        """
    )
    existing_idx = {r["indexname"] for r in indexes}
    if "budgets_company_id_code_key" not in existing_idx:
        await db.execute_raw(
            'CREATE UNIQUE INDEX "budgets_company_id_code_key" ON "budgets"("company_id", "code")'
        )
    if "budgets_company_id_fiscal_year_idx" not in existing_idx:
        await db.execute_raw(
            'CREATE INDEX "budgets_company_id_fiscal_year_idx" ON "budgets"("company_id", "fiscal_year")'
        )

    line_idx = await db.query_raw(
        """
        SELECT indexname FROM pg_indexes
        WHERE schemaname = 'public'
          AND tablename = 'budget_lines'
          AND indexname = 'budget_lines_budget_id_idx'
        """
    )
    if not line_idx:
        await db.execute_raw(
            'CREATE INDEX "budget_lines_budget_id_idx" ON "budget_lines"("budget_id")'
        )

    fks = await db.query_raw(
        """
        SELECT conname FROM pg_constraint
        WHERE conname IN ('budgets_company_id_fkey', 'budget_lines_budget_id_fkey')
        """
    )
    fk_names = {r["conname"] for r in fks}
    if "budgets_company_id_fkey" not in fk_names:
        await db.execute_raw(
            """
            ALTER TABLE "budgets"
            ADD CONSTRAINT "budgets_company_id_fkey"
            FOREIGN KEY ("company_id") REFERENCES "Company"("id")
            ON DELETE CASCADE ON UPDATE CASCADE
            """
        )
        print("added budgets_company_id_fkey")
    if "budget_lines_budget_id_fkey" not in fk_names:
        await db.execute_raw(
            """
            ALTER TABLE "budget_lines"
            ADD CONSTRAINT "budget_lines_budget_id_fkey"
            FOREIGN KEY ("budget_id") REFERENCES "budgets"("id")
            ON DELETE CASCADE ON UPDATE CASCADE
            """
        )
        print("added budget_lines_budget_id_fkey")

    await db.execute_raw(
        """
        INSERT INTO _prisma_migrations (
            id, checksum, finished_at, migration_name, logs,
            rolled_back_at, started_at, applied_steps_count
        )
        SELECT gen_random_uuid()::text, '', NOW(), '20260524130000_budget',
               NULL, NULL, NOW(), 1
        WHERE NOT EXISTS (
            SELECT 1 FROM _prisma_migrations
            WHERE migration_name = '20260524130000_budget'
        )
        """
    )
    print("budget migration complete")
    await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
