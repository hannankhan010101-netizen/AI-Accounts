#!/usr/bin/env python3
"""Document + GL linkage health for migrated tenant (go-live advisory)."""
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

MIGRATE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(MIGRATE_DIR))
from _tenant import tenant_id  # noqa: E402

CID = tenant_id()


async def main() -> int:
    db = Prisma()
    await db.connect()

    si_total = await db.salesinvoice.count(where={"companyId": CID})
    si_posted = await db.salesinvoice.count(
        where={"companyId": CID, "journalId": {"not": None}}
    )
    si_draft = await db.salesinvoice.count(
        where={"companyId": CID, "status": "draft", "journalId": None}
    )
    si_posted_orphan = await db.salesinvoice.count(
        where={"companyId": CID, "status": "posted", "journalId": None}
    )

    vi_total = await db.supplierbill.count(where={"companyId": CID})
    vi_posted = await db.supplierbill.count(
        where={"companyId": CID, "journalId": {"not": None}}
    )
    vi_draft = await db.supplierbill.count(
        where={"companyId": CID, "status": "draft", "journalId": None}
    )
    vi_posted_orphan = await db.supplierbill.count(
        where={"companyId": CID, "status": "posted", "journalId": None}
    )

    sr_draft = await db.salesreceipt.count(
        where={"companyId": CID, "status": "draft", "journalId": None}
    )
    vp_draft = await db.supplierpayment.count(
        where={"companyId": CID, "status": "draft", "journalId": None}
    )

    je_posted = await db.journal.count(
        where={"companyId": CID, "status": "posted"}
    )

    from app.repositories.journal_repository import JournalRepository

    tb_rows = await JournalRepository(db).trial_balance(company_id=CID, as_of_date=None)
    nominals_active = len(tb_rows)

    await db.disconnect()

    print(f"=== Migration health ({CID}) ===\n")
    print("Sales invoices:")
    print(f"  Total:              {si_total}")
    print(f"  With GL journal:    {si_posted}")
    print(f"  Draft (no journal): {si_draft}")
    print(f"  Posted orphan:      {si_posted_orphan}")
    print()
    print("Supplier bills:")
    print(f"  Total:              {vi_total}")
    print(f"  With GL journal:    {vi_posted}")
    print(f"  Draft (no journal): {vi_draft}")
    print(f"  Posted orphan:      {vi_posted_orphan}")
    print()
    print(f"  Draft sales receipts:    {sr_draft}")
    print(f"  Draft supplier payments: {vp_draft}")
    print()
    print(f"  Posted journals:         {je_posted}")
    print(f"  Nominals with activity:  {nominals_active}")

    issues = 0
    if si_posted_orphan or vi_posted_orphan:
        print("\n  WARNING: posted documents missing journalId — run migrate_posting.py")
        issues += 1
    if si_draft or vi_draft or sr_draft or vp_draft:
        print(
            "\n  NOTE: draft documents remain. For summary-GL migration (few active nominals),"
        )
        print(
            "  do NOT bulk-post all drafts - that duplicates AR/AP. Approve only documents"
        )
        print(
            "  that should have open-item GL, or leave drafts for operational workflow."
        )
    if not issues and not (si_draft or vi_draft):
        print("\n  MIGRATION HEALTH: PASS (no posted orphans; no stray drafts)")
        return 0
    if si_posted_orphan or vi_posted_orphan:
        return 1
    print("\n  MIGRATION HEALTH: REVIEW (drafts present - expected for some FA exports)")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
