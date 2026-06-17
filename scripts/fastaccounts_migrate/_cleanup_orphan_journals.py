#!/usr/bin/env python3
"""Remove duplicate SI/SB journals left by interrupted migrate_posting runs."""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "Backend"
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

if os.getenv("DIRECT_URL"):
    os.environ["DATABASE_URL"] = os.environ["DIRECT_URL"]

from prisma_generated import Prisma

CID = "cmpfl1itj000hqubj7rne8q5f"


async def cleanup(company_id: str, *, dry_run: bool) -> None:
    db = Prisma()
    await db.connect()

    for source_type, table, fk in (
        ("SALES_INVOICE", "sales_invoices", "journal_id"),
        ("SUPPLIER_BILL", "supplier_bills", "journal_id"),
    ):
        rows = await db.query_raw(
            f"""
            SELECT j.id
            FROM journals j
            WHERE j.company_id = $1
              AND j.source_type = $2
              AND j.source_id IS NOT NULL
              AND NOT EXISTS (
                SELECT 1 FROM {table} d
                WHERE d.id = j.source_id AND d.{fk} = j.id
              )
            """,
            company_id,
            source_type,
        )
        ids = [r["id"] for r in rows]
        print(f"{source_type}: {len(ids)} orphan journals")
        if dry_run or not ids:
            continue
        for jid in ids:
            await db.journalline.delete_many(where={"journalId": jid})
            await db.journal.delete(where={"id": jid})

    await db.disconnect()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--company-id", default=CID)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    asyncio.run(cleanup(args.company_id, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
