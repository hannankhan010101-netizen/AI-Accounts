#!/usr/bin/env python3
"""Link invoices/bills to existing journals by source_id (repair interrupted runs)."""
from __future__ import annotations

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

from app.domain import document_workflow as wf

CID = "cmpfl1itj000hqubj7rne8q5f"


async def repair(db: Prisma, company_id: str, source_type: str, model: str) -> int:
    linked = 0
    journals = await db.journal.find_many(
        where={"companyId": company_id, "sourceType": source_type, "sourceId": {"not": None}},
        order={"createdAt": "asc"},
    )
    seen: set[str] = set()
    for j in journals:
        sid = j.sourceId
        if not sid or sid in seen:
            continue
        seen.add(sid)
        if model == "invoice":
            doc = await db.salesinvoice.find_unique(where={"id": sid})
            if doc and doc.journalId is None:
                await db.salesinvoice.update(where={"id": sid}, data={"journalId": j.id})
                linked += 1
        else:
            doc = await db.supplierbill.find_unique(where={"id": sid})
            if doc and doc.journalId is None:
                await db.supplierbill.update(where={"id": sid}, data={"journalId": j.id})
                linked += 1
    return linked


async def main() -> None:
    db = Prisma()
    await db.connect()
    inv = await repair(db, CID, wf.SOURCE_SALES_INVOICE, "invoice")
    bill = await repair(db, CID, wf.SOURCE_SUPPLIER_BILL, "bill")
    print(f"linked invoices={inv} bills={bill}")
    orphans = await db.query_raw(
        """
        SELECT COUNT(*)::int AS n FROM journals j
        WHERE j.company_id = $1
          AND j.source_type = 'SALES_INVOICE'
          AND j.source_id IS NOT NULL
          AND NOT EXISTS (
            SELECT 1 FROM sales_invoices si
            WHERE si.id = j.source_id AND si.journal_id = j.id
          )
        """,
        CID,
    )
    print(f"orphan_si_journals={orphans[0]['n'] if orphans else 0}")
    await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
