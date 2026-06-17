#!/usr/bin/env python3
"""Backfill GL journals for migrated FA documents (status posted, journalId null)."""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import uuid
from decimal import Decimal
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2] / "Backend"
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

import os

if os.getenv("DIRECT_URL"):
    os.environ["DATABASE_URL"] = os.environ["DIRECT_URL"]

from prisma_generated import Prisma

from app.repositories.bank_repository import BankRepository
from app.repositories.coa_repository import CoaRepository
from app.repositories.document_number_repository import DocumentNumberRepository
from app.repositories.journal_repository import JournalRepository
from app.repositories.smart_settings_repository import SmartSettingsRepository
from app.repositories.taxes_config_repository import TaxesConfigRepository
from app.services.document_number_service import DocumentNumberService
from app.services.journal_service import JournalService
from app.services.posting_service import PostingService
from app.services.tax_calculation_service import TaxCalculationService
from app.domain import document_workflow as wf

DEFAULT_JSON = (
    Path(__file__).resolve().parents[1]
    / "fastaccounts_export"
    / "output"
    / "fastaccounts_labeled_data.json"
)
CID = "cmpfl1itj000hqubj7rne8q5f"

# Nafy-Pharma COA mapping (from migrated chart)
NAFY_POSTING_DEFAULTS: dict[str, str] = {
    "receivablesNominalCode": "230201",  # Debtors
    "salesNominalCode": "410101",  # Sales of Product Income
    "payablesNominalCode": "120101",  # Trade Creditors
    "purchasesNominalCode": "510204",  # Purchases
    "gstOutputNominalCode": "120301",  # General Sales Tax
    "gstInputNominalCode": "120301",
    "inventoryNominalCode": "230101",  # Stock
    "cogsNominalCode": "510204",
    "stockAdjustmentNominalCode": "510401",
    "bankNominalCode": "230909",  # Bank Of Punjab
}


def log(msg: str) -> None:
    print(msg, flush=True)


def build_services(db: Prisma) -> tuple[PostingService, TaxCalculationService, CoaRepository]:
    journals = JournalRepository(db)
    coa = CoaRepository(db)
    numbers = DocumentNumberService(
        document_number_repository=DocumentNumberRepository(db)
    )
    journal_service = JournalService(
        journal_repository=journals,
        document_number_service=numbers,
        coa_repository=coa,
    )
    posting = PostingService(
        journal_service=journal_service,
        smart_settings_repository=SmartSettingsRepository(db),
        bank_repository=BankRepository(db),
    )
    tax = TaxCalculationService(taxes_repository=TaxesConfigRepository(db))
    return posting, tax, coa


async def ensure_posting_defaults(db: Prisma, company_id: str) -> None:
    row = await db.smartsettings.find_unique(where={"companyId": company_id})
    payload: dict[str, Any] = {}
    if row and isinstance(row.payload, dict):
        payload = dict(row.payload)
    existing = payload.get("defaults")
    if isinstance(existing, dict) and existing.get("receivablesNominalCode"):
        log("  Posting defaults already configured — merging missing keys only")
        merged = {**NAFY_POSTING_DEFAULTS, **existing}
    else:
        merged = dict(NAFY_POSTING_DEFAULTS)
    payload["defaults"] = merged
    await db.execute_raw(
        """
        INSERT INTO smart_settings (id, company_id, payload, updated_at)
        VALUES (gen_random_uuid()::text, $1, $2::jsonb, NOW())
        ON CONFLICT (company_id)
        DO UPDATE SET payload = EXCLUDED.payload, updated_at = NOW()
        """,
        company_id,
        json.dumps(payload),
    )
    log(f"  Defaults set: AR={merged['receivablesNominalCode']} "
        f"Sales={merged['salesNominalCode']} AP={merged['payablesNominalCode']}")


async def verify_nominals(db: Prisma, company_id: str, codes: list[str]) -> list[str]:
    coa = CoaRepository(db)
    return await coa.missing_nominal_codes(company_id=company_id, codes=codes)


def line_payloads(lines: list) -> list[dict]:
    return [
        {
            "productCode": line.productCode,
            "quantity": line.quantity,
            "rate": line.rate,
            "gstCode": line.gstCode,
            "gstRate": line.gstRate,
        }
        for line in lines or []
    ]


def _has_line_tax(lines: list) -> bool:
    for line in lines or []:
        if line.gstCode:
            return True
        rate = line.gstRate
        if rate is not None and Decimal(str(rate)) > 0:
            return True
    return False


def _amounts_for_migration(total_amount, lines: list) -> tuple[Decimal, Decimal, list] | None:
    """Use header total when FA import has no GST (summary lines)."""
    if _has_line_tax(lines):
        return None
    amt = Decimal(str(total_amount))
    return amt, amt, []


async def _link_existing_journal(
    db: Prisma,
    *,
    doc_id: str,
    journal_id: str,
    table: str,
) -> None:
    if table == "invoice":
        await db.salesinvoice.update(where={"id": doc_id}, data={"journalId": journal_id})
    else:
        await db.supplierbill.update(where={"id": doc_id}, data={"journalId": journal_id})


async def _find_source_journal(
    db: Prisma, company_id: str, source_type: str, source_id: str
):
    return await db.journal.find_first(
        where={
            "companyId": company_id,
            "sourceType": source_type,
            "sourceId": source_id,
        },
        order={"createdAt": "asc"},
    )


async def post_sales_invoices(
    db: Prisma,
    company_id: str,
    *,
    limit: int | None,
    dry_run: bool,
) -> dict[str, int]:
    posting, tax, _coa = build_services(db)
    stats = {"posted": 0, "skipped": 0, "errors": 0}

    where = {"companyId": company_id, "journalId": None, "status": "posted"}
    total = await db.salesinvoice.count(where=where)
    log(f"  Sales invoices to link: {total}" + (f" (limit {limit})" if limit else ""))

    cursor: str | None = None
    processed = 0
    while True:
        batch = await db.salesinvoice.find_many(
            where=where,
            include={"lines": True},
            order={"id": "asc"},
            take=100,
            **({"cursor": {"id": cursor}, "skip": 1} if cursor else {}),
        )
        if not batch:
            break
        for inv in batch:
            if limit is not None and processed >= limit:
                return stats
            processed += 1
            if dry_run:
                stats["posted"] += 1
                continue
            try:
                existing = await _find_source_journal(
                    db, company_id, wf.SOURCE_SALES_INVOICE, inv.id
                )
                if existing:
                    await _link_existing_journal(
                        db, doc_id=inv.id, journal_id=existing.id, table="invoice"
                    )
                    stats["posted"] += 1
                    continue
                fast = _amounts_for_migration(inv.totalAmount, inv.lines or [])
                if fast is not None:
                    net_amount, gross_amount, tax_legs = fast
                else:
                    taxed = await tax.compute_sales_lines(
                        company_id=company_id, raw_lines=line_payloads(inv.lines or [])
                    )
                    net_amount, gross_amount, tax_legs = (
                        taxed.net_total,
                        taxed.gross_total,
                        taxed.tax_legs,
                    )
                journal = await posting.post_sales_invoice(
                    company_id=company_id,
                    invoice_date=inv.invoiceDate,
                    invoice_number=inv.invoiceNumber,
                    net_amount=net_amount,
                    gross_amount=gross_amount,
                    tax_legs=tax_legs,
                    source_id=inv.id,
                    correlation_id=str(uuid.uuid4()),
                )
                if journal is None:
                    stats["errors"] += 1
                    continue
                await db.salesinvoice.update(
                    where={"id": inv.id},
                    data={"journalId": journal.id},
                )
                stats["posted"] += 1
            except Exception as exc:
                stats["errors"] += 1
                if stats["errors"] <= 3:
                    log(f"    invoice error ({inv.invoiceNumber}): {exc}")
            if processed % 100 == 0:
                log(f"    invoices: {processed}/{total} posted={stats['posted']} err={stats['errors']}")
        cursor = batch[-1].id
        if limit is not None and processed >= limit:
            break
    return stats


async def post_supplier_bills(
    db: Prisma,
    company_id: str,
    *,
    limit: int | None,
    dry_run: bool,
) -> dict[str, int]:
    posting, tax, _coa = build_services(db)
    stats = {"posted": 0, "skipped": 0, "errors": 0}

    where = {"companyId": company_id, "journalId": None, "status": "posted"}
    total = await db.supplierbill.count(where=where)
    log(f"  Supplier bills to link: {total}" + (f" (limit {limit})" if limit else ""))

    cursor: str | None = None
    processed = 0
    while True:
        batch = await db.supplierbill.find_many(
            where=where,
            include={"lines": True},
            order={"id": "asc"},
            take=100,
            **({"cursor": {"id": cursor}, "skip": 1} if cursor else {}),
        )
        if not batch:
            break
        for bill in batch:
            if limit is not None and processed >= limit:
                return stats
            processed += 1
            if dry_run:
                stats["posted"] += 1
                continue
            try:
                existing = await _find_source_journal(
                    db, company_id, wf.SOURCE_SUPPLIER_BILL, bill.id
                )
                if existing:
                    await _link_existing_journal(
                        db, doc_id=bill.id, journal_id=existing.id, table="bill"
                    )
                    stats["posted"] += 1
                    continue
                fast = _amounts_for_migration(bill.totalAmount, bill.lines or [])
                if fast is not None:
                    net_amount, gross_amount, tax_legs = fast
                else:
                    taxed = await tax.compute_purchase_lines(
                        company_id=company_id, raw_lines=line_payloads(bill.lines or [])
                    )
                    net_amount, gross_amount, tax_legs = (
                        taxed.net_total,
                        taxed.gross_total,
                        taxed.tax_legs,
                    )
                journal = await posting.post_supplier_bill(
                    company_id=company_id,
                    bill_date=bill.billDate,
                    bill_number=bill.billNumber,
                    net_amount=net_amount,
                    gross_amount=gross_amount,
                    tax_legs=tax_legs,
                    source_id=bill.id,
                    correlation_id=str(uuid.uuid4()),
                )
                if journal is None:
                    stats["errors"] += 1
                    continue
                await db.supplierbill.update(
                    where={"id": bill.id},
                    data={"journalId": journal.id},
                )
                stats["posted"] += 1
            except Exception as exc:
                stats["errors"] += 1
                if stats["errors"] <= 3:
                    log(f"    bill error ({bill.billNumber}): {exc}")
            if processed % 50 == 0:
                log(f"    bills: {processed}/{total} posted={stats['posted']} err={stats['errors']}")
        cursor = batch[-1].id
        if limit is not None and processed >= limit:
            break
    return stats


async def run(
    company_id: str,
    *,
    limit: int | None,
    dry_run: bool,
    invoices_only: bool,
    bills_only: bool,
) -> None:
    db = Prisma()
    await db.connect()

    company = await db.company.find_unique(where={"id": company_id})
    if not company:
        raise SystemExit(f"Company not found: {company_id}")
    log(f"GL posting migration: {company.name} ({company_id})")

    log("[1/3] Configure posting defaults...")
    if not dry_run:
        await ensure_posting_defaults(db, company_id)
        missing = await verify_nominals(
            db, company_id, list(NAFY_POSTING_DEFAULTS.values())
        )
        if missing:
            raise SystemExit(f"Missing nominal codes on COA: {missing}")

    inv_stats: dict[str, int] = {}
    bill_stats: dict[str, int] = {}

    if not bills_only:
        log("[2/3] Link sales invoice journals...")
        inv_stats = await post_sales_invoices(
            db, company_id, limit=limit, dry_run=dry_run
        )
        log(f"  Invoices done: {inv_stats}")

    if not invoices_only:
        log("[3/3] Link supplier bill journals...")
        bill_stats = await post_supplier_bills(
            db, company_id, limit=limit, dry_run=dry_run
        )
        log(f"  Bills done: {bill_stats}")

    if not dry_run:
        inv_with_j = await db.salesinvoice.count(
            where={"companyId": company_id, "journalId": {"not": None}}
        )
        bill_with_j = await db.supplierbill.count(
            where={"companyId": company_id, "journalId": {"not": None}}
        )
        j_total = await db.journal.count(where={"companyId": company_id})
        log("\n=== Verification ===")
        log(f"  invoices with journalId: {inv_with_j}")
        log(f"  bills with journalId: {bill_with_j}")
        log(f"  total journals: {j_total}")

    await db.disconnect()


def main() -> None:
    p = argparse.ArgumentParser(description="Backfill GL for migrated FA documents")
    p.add_argument("--company-id", default=CID)
    p.add_argument("--limit", type=int, default=None, help="Max docs per type (for testing)")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--invoices-only", action="store_true")
    p.add_argument("--bills-only", action="store_true")
    args = p.parse_args()
    asyncio.run(
        run(
            args.company_id,
            limit=args.limit,
            dry_run=args.dry_run,
            invoices_only=args.invoices_only,
            bills_only=args.bills_only,
        )
    )


if __name__ == "__main__":
    main()
