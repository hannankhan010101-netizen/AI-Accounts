#!/usr/bin/env python3
"""Post draft SI/VI/SR/VP documents to GL for a tenant (import / template cleanup).

WARNING: For tenants migrated with summary GL (few nominals, TB already balanced),
bulk posting all drafts creates duplicate AR/AP detail. Run _migration_health.py first.
"""
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
from app.repositories.sales_receipt_repository import SalesReceiptRepository
from app.repositories.supplier_payment_repository import SupplierPaymentRepository
from app.services.import_posting_context import build_import_posting_stack

MIGRATE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(MIGRATE_DIR))
from _tenant import tenant_id  # noqa: E402

DEFAULT_CID = tenant_id()


async def main() -> int:
    parser = argparse.ArgumentParser(description="Post draft settlements and approve draft invoices/bills")
    parser.add_argument("--company-id", default=DEFAULT_CID)
    parser.add_argument("--limit", type=int, default=500, help="Max docs per type")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--i-understand-summary-gl-risk",
        action="store_true",
        help="Required for live post on summary-GL migrated tenants",
    )
    args = parser.parse_args()
    if not args.dry_run and not args.i_understand_summary_gl_risk:
        print(
            "Refusing live post: add --i-understand-summary-gl-risk after reviewing "
            "_migration_health.py (summary GL tenants may double-count AR/AP)."
        )
        return 2
    cid = args.company_id

    db = Prisma()
    await db.connect()
    engine, posting = build_import_posting_stack(db)
    sr_repo = SalesReceiptRepository(db)
    vp_repo = SupplierPaymentRepository(db)

    stats = {"si": 0, "vi": 0, "sr": 0, "vp": 0, "errors": []}

    invoices = await db.salesinvoice.find_many(
        where={"companyId": cid, "status": "draft", "journalId": None},
        take=args.limit,
    )
    for inv in invoices:
        if args.dry_run:
            stats["si"] += 1
            continue
        try:
            await engine.approve_sales_invoice(company_id=cid, invoice_id=inv.id)
            stats["si"] += 1
        except Exception as exc:  # noqa: BLE001
            stats["errors"].append(f"SI {inv.invoiceNumber}: {exc}")

    bills = await db.supplierbill.find_many(
        where={"companyId": cid, "status": "draft", "journalId": None},
        take=args.limit,
    )
    for bill in bills:
        if args.dry_run:
            stats["vi"] += 1
            continue
        try:
            await engine.approve_supplier_bill(company_id=cid, bill_id=bill.id)
            stats["vi"] += 1
        except Exception as exc:  # noqa: BLE001
            stats["errors"].append(f"VI {bill.billNumber}: {exc}")

    receipts = await db.salesreceipt.find_many(
        where={"companyId": cid, "status": "draft", "journalId": None},
        take=args.limit,
    )
    for rcpt in receipts:
        if args.dry_run:
            stats["sr"] += 1
            continue
        try:
            journal = await posting.post_sales_receipt(
                company_id=cid,
                receipt_date=rcpt.receiptDate,
                receipt_number=rcpt.receiptNumber,
                bank_account_id=rcpt.bankAccountId,
                total_amount=rcpt.totalAmount,
            )
            if journal is None:
                stats["errors"].append(f"SR {rcpt.receiptNumber}: posting returned None")
                continue
            await sr_repo.link_receipt_journal(receipt_id=rcpt.id, journal_id=journal.id)
            stats["sr"] += 1
        except Exception as exc:  # noqa: BLE001
            stats["errors"].append(f"SR {rcpt.receiptNumber}: {exc}")

    payments = await db.supplierpayment.find_many(
        where={"companyId": cid, "status": "draft", "journalId": None},
        take=args.limit,
    )
    for pay in payments:
        if args.dry_run:
            stats["vp"] += 1
            continue
        try:
            journal = await posting.post_supplier_payment(
                company_id=cid,
                payment_date=pay.paymentDate,
                voucher_number=pay.voucherNumber,
                bank_account_id=pay.bankAccountId,
                total_amount=pay.totalAmount,
            )
            if journal is None:
                stats["errors"].append(f"VP {pay.voucherNumber}: posting returned None")
                continue
            await vp_repo.link_payment_journal(payment_id=pay.id, journal_id=journal.id)
            stats["vp"] += 1
        except Exception as exc:  # noqa: BLE001
            stats["errors"].append(f"VP {pay.voucherNumber}: {exc}")

    await db.disconnect()

    mode = "DRY-RUN" if args.dry_run else "POSTED"
    print(f"=== Bulk draft post ({cid}) [{mode}] ===\n")
    print(f"  Sales invoices:    {stats['si']}")
    print(f"  Supplier bills:    {stats['vi']}")
    print(f"  Sales receipts:    {stats['sr']}")
    print(f"  Supplier payments: {stats['vp']}")
    if stats["errors"]:
        print(f"\n  Errors ({len(stats['errors'])}):")
        for err in stats["errors"][:20]:
            print(f"    {err}")
        if len(stats["errors"]) > 20:
            print(f"    ... and {len(stats['errors']) - 20} more")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
