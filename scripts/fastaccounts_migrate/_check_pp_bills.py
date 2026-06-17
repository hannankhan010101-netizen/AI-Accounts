#!/usr/bin/env python3
"""Find supplier bills present only in purchase_payments export module."""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

MIGRATE_DIR = Path(__file__).resolve().parent
ROOT = MIGRATE_DIR.parents[1] / "Backend"
sys.path.insert(0, str(MIGRATE_DIR))
sys.path.insert(0, str(ROOT / "src"))

from migrate_aggregate import normalize_row  # noqa: E402

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

import os

if os.getenv("DIRECT_URL"):
    os.environ["DATABASE_URL"] = os.environ["DIRECT_URL"]

from prisma_generated import Prisma  # noqa: E402

DEFAULT_JSON = MIGRATE_DIR.parent / "fastaccounts_export" / "output" / "fastaccounts_labeled_data.json"
CID = "cmpfl1itj000hqubj7rne8q5f"


def export_bills(sections: dict) -> set[str]:
    out: set[str] = set()
    for r in sections.get("purchases_all", []):
        row = normalize_row(r)
        if row and ("invoice" in row["doc_type"].lower() or "bill" in row["doc_type"].lower()):
            out.add(row["doc_no"])
    for r in sections.get("purchase_bills", []):
        n = str(r.get("Invoice No") or "").strip()
        if n:
            out.add(n)
    return out


def pp_bills(sections: dict) -> set[str]:
    out: set[str] = set()
    for r in sections.get("purchase_payments", []):
        if str(r.get("Type") or "").lower() == "bill":
            n = str(r.get("Invoice No") or "").strip()
            if n:
                out.add(n)
    return out


async def main() -> None:
    sections = {
        s["moduleKey"]: s["records"]
        for s in json.loads(DEFAULT_JSON.read_text(encoding="utf-8"))["sections"]
    }
    only_pp = pp_bills(sections) - export_bills(sections)

    db = Prisma()
    await db.connect()
    db_nos = {
        b.billNumber
        for b in await db.supplierbill.find_many(where={"companyId": CID})
    }
    await db.disconnect()

    missing = sorted(only_pp - db_nos)
    print(f"Bills only in purchase_payments module: {len(only_pp)}")
    print(f"Missing from DB: {len(missing)}")
    total = 0.0
    for no in missing:
        for r in sections["purchase_payments"]:
            if str(r.get("Invoice No")) == no:
                amt = float(str(r.get("Total") or "0").replace(",", "") or 0)
                total += amt
                print(
                    f"  {no}  supplier={r.get('Account No')}  "
                    f"{r.get('Contact Name')}  total={r.get('Total')}"
                )
                break
    print(f"Total missing amount: {total:,.2f}")


if __name__ == "__main__":
    asyncio.run(main())
