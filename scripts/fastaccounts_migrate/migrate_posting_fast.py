#!/usr/bin/env python3
"""Fast bulk GL backfill via batched SQL (resume-safe, idempotent)."""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import uuid
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2] / "Backend"
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

if os.getenv("DIRECT_URL"):
    os.environ["DATABASE_URL"] = os.environ["DIRECT_URL"]

from prisma_generated import Prisma

from app.domain import document_workflow as wf
from app.repositories.coa_repository import CoaRepository

CID = "cmpfl1itj000hqubj7rne8q5f"
BATCH = 100

SI_DEFAULTS = {"ar": "230201", "cr": "410101"}
SB_DEFAULTS = {"dr": "510204", "cr": "120101"}


def log(msg: str) -> None:
    print(msg, flush=True)


async def reserve_journal_numbers(db: Prisma, company_id: str, count: int) -> list[int]:
    rows = await db.query_raw(
        """
        UPDATE document_number_sequences
        SET next_value = next_value + $2
        WHERE company_id = $1 AND key = 'journal'
        RETURNING next_value - $2 AS block_start
        """,
        company_id,
        count,
    )
    if rows:
        start = int(rows[0]["block_start"])
        return list(range(start, start + count))

    await db.execute_raw(
        """
        INSERT INTO document_number_sequences (id, company_id, key, next_value)
        VALUES (gen_random_uuid()::text, $1, 'journal', $2 + 1)
        ON CONFLICT (company_id, key) DO UPDATE
        SET next_value = document_number_sequences.next_value + $2
        """,
        company_id,
        count,
    )
    rows = await db.query_raw(
        """
        SELECT next_value - $2 AS block_start
        FROM document_number_sequences
        WHERE company_id = $1 AND key = 'journal'
        """,
        company_id,
        count,
    )
    start = int(rows[0]["block_start"])
    return list(range(start, start + count))


async def bulk_post_sales_invoices(
    db: Prisma,
    company_id: str,
    *,
    limit: int | None,
    dry_run: bool,
    nominal_ids: dict[str, str],
) -> dict[str, int]:
    stats = {"posted": 0, "linked": 0, "errors": 0}
    ar_code = SI_DEFAULTS["ar"]
    sales_code = SI_DEFAULTS["cr"]
    ar_nid = nominal_ids.get(ar_code)
    sales_nid = nominal_ids.get(sales_code)

    where = {"companyId": company_id, "journalId": None, "status": "posted"}
    total = await db.salesinvoice.count(where=where)
    log(f"  Sales invoices remaining: {total}" + (f" (limit {limit})" if limit else ""))

    processed = 0
    while True:
        if limit is not None and processed >= limit:
            break
        take = BATCH if limit is None else min(BATCH, limit - processed)
        batch = await db.salesinvoice.find_many(
            where=where,
            order={"id": "asc"},
            take=take,
        )
        if not batch:
            break

        to_create: list[Any] = []
        existing_map: dict[str, str] = {}
        if not dry_run:
            src_ids = [inv.id for inv in batch]
            found = await db.journal.find_many(
                where={
                    "companyId": company_id,
                    "sourceType": wf.SOURCE_SALES_INVOICE,
                    "sourceId": {"in": src_ids},
                },
                order={"createdAt": "asc"},
            )
            for j in found:
                if j.sourceId and j.sourceId not in existing_map:
                    existing_map[j.sourceId] = j.id

        for inv in batch:
            jid = existing_map.get(inv.id)
            if jid:
                if not dry_run:
                    await db.salesinvoice.update(
                        where={"id": inv.id}, data={"journalId": jid}
                    )
                stats["linked"] += 1
                continue
            to_create.append(inv)

        if not to_create:
            processed += len(batch)
            continue

        if dry_run:
            stats["posted"] += len(to_create)
            processed += len(batch)
            continue

        try:
            numbers = await reserve_journal_numbers(db, company_id, len(to_create))
            j_ids = [str(uuid.uuid4()) for _ in to_create]
            inv_ids = [inv.id for inv in to_create]
            j_nums = [str(n) for n in numbers]
            j_dates = [inv.invoiceDate.isoformat() for inv in to_create]
            refs = [f"SI {inv.invoiceNumber}" for inv in to_create]
            amounts = [str(inv.totalAmount) for inv in to_create]

            await db.execute_raw(
                """
                INSERT INTO journals (
                    id, company_id, journal_number, journal_date, ref_no,
                    total_amount, status, source_type, source_id, created_at
                )
                SELECT
                    u.jid, $1, u.jnum, u.jdate::timestamptz, u.ref,
                    u.amt::numeric, 'posted', 'SALES_INVOICE', u.sid, NOW()
                FROM unnest(
                    $2::text[], $3::text[], $4::text[], $5::text[], $6::text[], $7::text[]
                ) AS u(jid, jnum, jdate, ref, amt, sid)
                """,
                company_id,
                j_ids,
                j_nums,
                j_dates,
                refs,
                amounts,
                inv_ids,
            )

            line_ids_dr = [str(uuid.uuid4()) for _ in to_create]
            line_ids_cr = [str(uuid.uuid4()) for _ in to_create]
            debits = amounts
            zeros = ["0"] * len(to_create)

            await db.execute_raw(
                """
                INSERT INTO journal_lines (
                    id, journal_id, nominal_code, nominal_account_id, debit, credit
                )
                SELECT u.lid, u.jid, $7, $8, u.debit::numeric, 0
                FROM unnest($2::text[], $3::text[], $4::text[]) AS u(lid, jid, debit)
                UNION ALL
                SELECT u.lid, u.jid, $9, $10, 0, u.credit::numeric
                FROM unnest($5::text[], $3::text[], $6::text[]) AS u(lid, jid, credit)
                """,
                company_id,
                line_ids_dr,
                j_ids,
                debits,
                line_ids_cr,
                amounts,
                ar_code,
                ar_nid,
                sales_code,
                sales_nid,
            )

            await db.execute_raw(
                """
                UPDATE sales_invoices si
                SET journal_id = u.jid
                FROM unnest($2::text[], $3::text[]) AS u(sid, jid)
                WHERE si.id = u.sid
                """,
                company_id,
                inv_ids,
                j_ids,
            )
            stats["posted"] += len(to_create)
        except Exception as exc:
            stats["errors"] += len(to_create)
            log(f"    batch error: {exc}")
        processed += len(batch)
        if processed % 500 == 0 or len(batch) < take:
            log(f"    invoices: {processed} posted={stats['posted']} linked={stats['linked']} err={stats['errors']}")

    return stats


async def bulk_post_supplier_bills(
    db: Prisma,
    company_id: str,
    *,
    limit: int | None,
    dry_run: bool,
    nominal_ids: dict[str, str],
) -> dict[str, int]:
    stats = {"posted": 0, "linked": 0, "errors": 0}
    purch_code = SB_DEFAULTS["dr"]
    ap_code = SB_DEFAULTS["cr"]
    purch_nid = nominal_ids.get(purch_code)
    ap_nid = nominal_ids.get(ap_code)

    where = {"companyId": company_id, "journalId": None, "status": "posted"}
    total = await db.supplierbill.count(where=where)
    log(f"  Supplier bills remaining: {total}" + (f" (limit {limit})" if limit else ""))

    processed = 0
    while True:
        if limit is not None and processed >= limit:
            break
        take = BATCH if limit is None else min(BATCH, limit - processed)
        batch = await db.supplierbill.find_many(where=where, order={"id": "asc"}, take=take)
        if not batch:
            break

        to_create: list[Any] = []
        existing_map: dict[str, str] = {}
        if not dry_run:
            src_ids = [b.id for b in batch]
            found = await db.journal.find_many(
                where={
                    "companyId": company_id,
                    "sourceType": wf.SOURCE_SUPPLIER_BILL,
                    "sourceId": {"in": src_ids},
                },
                order={"createdAt": "asc"},
            )
            for j in found:
                if j.sourceId and j.sourceId not in existing_map:
                    existing_map[j.sourceId] = j.id

        for bill in batch:
            jid = existing_map.get(bill.id)
            if jid:
                if not dry_run:
                    await db.supplierbill.update(
                        where={"id": bill.id}, data={"journalId": jid}
                    )
                stats["linked"] += 1
                continue
            to_create.append(bill)

        if not to_create:
            processed += len(batch)
            continue

        if dry_run:
            stats["posted"] += len(to_create)
            processed += len(batch)
            continue

        try:
            numbers = await reserve_journal_numbers(db, company_id, len(to_create))
            j_ids = [str(uuid.uuid4()) for _ in to_create]
            bill_ids = [b.id for b in to_create]
            j_nums = [str(n) for n in numbers]
            j_dates = [b.billDate.isoformat() for b in to_create]
            refs = [f"SB {b.billNumber}" for b in to_create]
            amounts = [str(b.totalAmount) for b in to_create]

            await db.execute_raw(
                """
                INSERT INTO journals (
                    id, company_id, journal_number, journal_date, ref_no,
                    total_amount, status, source_type, source_id, created_at
                )
                SELECT
                    u.jid, $1, u.jnum, u.jdate::timestamptz, u.ref,
                    u.amt::numeric, 'posted', 'SUPPLIER_BILL', u.sid, NOW()
                FROM unnest(
                    $2::text[], $3::text[], $4::text[], $5::text[], $6::text[], $7::text[]
                ) AS u(jid, jnum, jdate, ref, amt, sid)
                """,
                company_id,
                j_ids,
                j_nums,
                j_dates,
                refs,
                amounts,
                bill_ids,
            )

            line_ids_dr = [str(uuid.uuid4()) for _ in to_create]
            line_ids_cr = [str(uuid.uuid4()) for _ in to_create]

            await db.execute_raw(
                """
                INSERT INTO journal_lines (
                    id, journal_id, nominal_code, nominal_account_id, debit, credit
                )
                SELECT u.lid, u.jid, $7, $8, u.debit::numeric, 0
                FROM unnest($2::text[], $3::text[], $4::text[]) AS u(lid, jid, debit)
                UNION ALL
                SELECT u.lid, u.jid, $9, $10, 0, u.credit::numeric
                FROM unnest($5::text[], $3::text[], $6::text[]) AS u(lid, jid, credit)
                """,
                company_id,
                line_ids_dr,
                j_ids,
                amounts,
                line_ids_cr,
                amounts,
                purch_code,
                purch_nid,
                ap_code,
                ap_nid,
            )

            await db.execute_raw(
                """
                UPDATE supplier_bills sb
                SET journal_id = u.jid
                FROM unnest($2::text[], $3::text[]) AS u(sid, jid)
                WHERE sb.id = u.sid
                """,
                company_id,
                bill_ids,
                j_ids,
            )
            stats["posted"] += len(to_create)
        except Exception as exc:
            stats["errors"] += len(to_create)
            log(f"    batch error: {exc}")

        processed += len(batch)
        if processed % 200 == 0 or len(batch) < take:
            log(f"    bills: {processed} posted={stats['posted']} linked={stats['linked']} err={stats['errors']}")

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
    log(f"Fast GL posting: {company.name} ({company_id})")

    coa = CoaRepository(db)
    codes = list({SI_DEFAULTS["ar"], SI_DEFAULTS["cr"], SB_DEFAULTS["dr"], SB_DEFAULTS["cr"]})
    nominal_ids = await coa.nominal_ids_by_codes(company_id=company_id, codes=codes)
    missing = [c for c in codes if c not in nominal_ids]
    if missing and not dry_run:
        raise SystemExit(f"Missing nominal codes: {missing}")

    if not bills_only:
        log("[1/2] Sales invoices...")
        si = await bulk_post_sales_invoices(
            db, company_id, limit=limit, dry_run=dry_run, nominal_ids=nominal_ids
        )
        log(f"  Done: {si}")

    if not invoices_only:
        log("[2/2] Supplier bills...")
        sb = await bulk_post_supplier_bills(
            db, company_id, limit=limit, dry_run=dry_run, nominal_ids=nominal_ids
        )
        log(f"  Done: {sb}")

    if not dry_run:
        inv_j = await db.salesinvoice.count(
            where={"companyId": company_id, "journalId": {"not": None}}
        )
        bill_j = await db.supplierbill.count(
            where={"companyId": company_id, "journalId": {"not": None}}
        )
        j_total = await db.journal.count(where={"companyId": company_id})
        log("\n=== Verification ===")
        log(f"  invoices with journalId: {inv_j}")
        log(f"  bills with journalId: {bill_j}")
        log(f"  total journals: {j_total}")

    await db.disconnect()


def main() -> None:
    p = argparse.ArgumentParser(description="Fast bulk GL backfill")
    p.add_argument("--company-id", default=CID)
    p.add_argument("--limit", type=int, default=None)
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
