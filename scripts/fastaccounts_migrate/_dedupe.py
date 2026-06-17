#!/usr/bin/env python3
"""Remove duplicate sales invoices and supplier bills (same number per company)."""
from __future__ import annotations

import argparse
import asyncio
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "Backend"
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

import os

if os.getenv("DIRECT_URL"):
    os.environ["DATABASE_URL"] = os.environ["DIRECT_URL"]

from prisma_generated import Prisma

DEFAULT_CID = "cmpfl1itj000hqubj7rne8q5f"


def pick_keeper(rows: list) -> tuple[str, list[str]]:
    """Keep earliest createdAt; tie-break by id."""
    sorted_rows = sorted(rows, key=lambda r: (r.createdAt, r.id))
    keeper = sorted_rows[0]
    dupes = [r.id for r in sorted_rows[1:]]
    return keeper.id, dupes


async def dedupe_invoices(db: Prisma, company_id: str, dry_run: bool) -> int:
    invs = await db.salesinvoice.find_many(where={"companyId": company_id})
    by_no: dict[str, list] = defaultdict(list)
    for inv in invs:
        by_no[inv.invoiceNumber].append(inv)

    removed = 0
    for _no, group in by_no.items():
        if len(group) < 2:
            continue
        _keeper_id, dupe_ids = pick_keeper(group)
        for dupe_id in dupe_ids:
            if dry_run:
                removed += 1
                continue
            await db.salesreceiptallocation.delete_many(
                where={"salesInvoiceId": dupe_id},
            )
            await db.salesinvoice.delete(where={"id": dupe_id})
            removed += 1
    return removed


async def dedupe_bills(db: Prisma, company_id: str, dry_run: bool) -> int:
    bills = await db.supplierbill.find_many(where={"companyId": company_id})
    by_no: dict[str, list] = defaultdict(list)
    for bill in bills:
        by_no[bill.billNumber].append(bill)

    removed = 0
    for _no, group in by_no.items():
        if len(group) < 2:
            continue
        _keeper_id, dupe_ids = pick_keeper(group)
        for dupe_id in dupe_ids:
            if dry_run:
                removed += 1
                continue
            await db.supplierpaymentallocation.delete_many(
                where={"supplierBillId": dupe_id},
            )
            await db.supplierbill.delete(where={"id": dupe_id})
            removed += 1
    return removed


async def dedupe_bank_payments(db: Prisma, company_id: str, dry_run: bool) -> int:
    rows = await db.bankpayment.find_many(where={"companyId": company_id})
    by_key: dict[str, list] = defaultdict(list)
    for row in rows:
        key = f"{row.voucherNumber}|{row.nominalCode or ''}|{row.totalAmount}"
        by_key[key].append(row)

    removed = 0
    for _key, group in by_key.items():
        if len(group) < 2:
            continue
        _keeper_id, dupe_ids = pick_keeper(group)
        for dupe_id in dupe_ids:
            if dry_run:
                removed += 1
                continue
            await db.bankpayment.delete(where={"id": dupe_id})
            removed += 1
    return removed


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--company-id", default=DEFAULT_CID)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    db = Prisma()
    await db.connect()

    inv_removed = await dedupe_invoices(db, args.company_id, args.dry_run)
    bill_removed = await dedupe_bills(db, args.company_id, args.dry_run)
    pay_removed = await dedupe_bank_payments(db, args.company_id, args.dry_run)

    mode = "would remove" if args.dry_run else "removed"
    print(f"{mode} duplicate invoices: {inv_removed}")
    print(f"{mode} duplicate bills: {bill_removed}")
    print(f"{mode} duplicate bank payments: {pay_removed}")

    if not args.dry_run:
        invs = await db.salesinvoice.count(where={"companyId": args.company_id})
        bills = await db.supplierbill.count(where={"companyId": args.company_id})
        pays = await db.bankpayment.count(where={"companyId": args.company_id})
        print(f"final invoices: {invs}")
        print(f"final bills: {bills}")
        print(f"final bank_payments: {pays}")

    await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
