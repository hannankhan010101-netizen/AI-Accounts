#!/usr/bin/env python3
"""Trial balance integrity check for migrated tenant (go-live gate)."""
from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "Backend"
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")
if os.getenv("DIRECT_URL"):
    os.environ["DATABASE_URL"] = os.environ["DIRECT_URL"]

from prisma_generated import Prisma
from app.repositories.journal_repository import JournalRepository

MIGRATE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(MIGRATE_DIR))
from _tenant import tenant_id  # noqa: E402

CID = tenant_id()
TOLERANCE = Decimal("0.0001")


async def main() -> None:
    as_of_raw = sys.argv[1] if len(sys.argv) > 1 else None
    as_of = (
        datetime.fromisoformat(as_of_raw.replace("Z", "+00:00"))
        if as_of_raw
        else None
    )

    db = Prisma()
    await db.connect()
    repo = JournalRepository(db)

    posted_count = await db.journal.count(
        where={"companyId": CID, "status": "posted"},
    )
    draft_count = await db.journal.count(
        where={"companyId": CID, "status": "draft"},
    )

    rows = await repo.trial_balance(company_id=CID, as_of_date=as_of)
    total_debit = sum(Decimal(r["debit"]) for r in rows)
    total_credit = sum(Decimal(r["credit"]) for r in rows)
    diff = total_debit - total_credit

    nonzero = [
        r
        for r in rows
        if abs(Decimal(r["balance"])) > TOLERANCE
    ]
    nonzero.sort(key=lambda r: abs(Decimal(r["balance"])), reverse=True)

    await db.disconnect()

    label = as_of.date().isoformat() if as_of else "all dates"
    print(f"=== Trial balance spot check ({CID}) as of {label} ===\n")
    print(f"  Posted journals: {posted_count}")
    print(f"  Draft journals:  {draft_count}")
    print(f"  Nominals with activity: {len(rows)}")
    print(f"  Total debit:  {total_debit}")
    print(f"  Total credit: {total_credit}")
    print(f"  Debit - credit: {diff}")

    balanced = abs(diff) <= TOLERANCE
    print(f"\n  TB balanced: {'YES' if balanced else 'NO — investigate GL'}")

    if nonzero:
        print("\n  Top balances (by |balance|):")
        for r in nonzero[:15]:
            print(
                f"    {r['nominalCode']:8}  {r.get('name') or '':30}  "
                f"bal={r['balance']}"
            )

    sys.exit(0 if balanced else 1)


if __name__ == "__main__":
    asyncio.run(main())
