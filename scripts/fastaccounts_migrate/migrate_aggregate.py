#!/usr/bin/env python3
"""Import sales_all + purchases_all from FastAccounts complete export (mixed column formats)."""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2] / "Backend"
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

# Bulk migrations need session pooler (5432), not transaction pooler (6543).
import os
if os.getenv("DIRECT_URL"):
    os.environ["DATABASE_URL"] = os.environ["DIRECT_URL"]

from prisma_generated import Prisma

DEFAULT_JSON = (
    Path(__file__).resolve().parents[1]
    / "fastaccounts_export"
    / "output"
    / "fastaccounts_labeled_data.json"
)
CID = "cmpfl1itj000hqubj7rne8q5f"


def log(msg: str) -> None:
    print(msg, flush=True)


def parse_decimal(val: Any) -> Decimal:
    if val is None:
        return Decimal(0)
    s = str(val).replace(",", "").strip()
    if not s:
        return Decimal(0)
    try:
        return abs(Decimal(s))
    except InvalidOperation:
        return Decimal(0)


def parse_date(val: Any) -> datetime:
    s = str(val or "").strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return datetime.now(timezone.utc)


def col(r: dict, i: int) -> str:
    return str(r.get(f"col_{i}") or r.get(f"Col {i}") or "").strip()


def _looks_like_doc_type(s: str) -> bool:
    lower = s.lower()
    return any(k in lower for k in ("invoice", "receipt", "payment", "credit", "bill"))


def normalize_row(r: dict[str, Any]) -> dict[str, Any] | None:
    """Unified view across col_* and numeric-key DataTables rows."""
    if col(r, 0) or r.get("col_0") is not None:
        c3, c4 = col(r, 3), col(r, 4)
        if _looks_like_doc_type(c3):
            return {
                "date": col(r, 1),
                "party_key": col(r, 2),
                "contact_name": col(r, 2),
                "doc_type": c3,
                "doc_no": c4 or col(r, 0),
                "amount": parse_decimal(col(r, 8) or col(r, 7)),
            }
        return {
            "date": col(r, 1),
            "party_key": col(r, 2),
            "contact_name": col(r, 3),
            "doc_type": c4,
            "doc_no": col(r, 5) or c4 or col(r, 0),
            "amount": parse_decimal(col(r, 8) or col(r, 7)),
        }
    if r.get("1") is not None or r.get("2") is not None:
        f1 = str(r.get("1") or "").strip()
        f2 = str(r.get("2") or "").strip()
        f3 = str(r.get("3") or "").strip()
        f4 = str(r.get("4") or "").strip()
        f5 = str(r.get("5") or "").strip()
        # Purchase: 1=date, 2=supplier, 3=type, 4=docNo
        if _looks_like_doc_type(f3):
            return {
                "date": f1,
                "party_key": f2,
                "contact_name": f2,
                "doc_type": f3,
                "doc_no": f4 or f5,
                "amount": parse_decimal(r.get("8") or r.get("9") or r.get("7")),
            }
        # Sales receipt: 1=date, 2=account, 3=contact, 4=type, 5=docNo
        if _looks_like_doc_type(f4):
            return {
                "date": f1,
                "party_key": f2,
                "contact_name": f3,
                "doc_type": f4,
                "doc_no": f5 or f4,
                "amount": parse_decimal(r.get("8") or r.get("9") or r.get("7")),
            }
        return {
            "date": f1,
            "party_key": f2,
            "contact_name": f3,
            "doc_type": f4,
            "doc_no": f5 or f4,
            "amount": parse_decimal(r.get("8") or r.get("9") or r.get("7")),
        }
    return None


async def preload(db: Prisma, company_id: str) -> dict[str, Any]:
    log("Preloading lookups...")
    customers = await db.customer.find_many(where={"companyId": company_id})
    suppliers = await db.supplier.find_many(where={"companyId": company_id})
    banks = await db.bankaccount.find_many(where={"companyId": company_id})

    cust_by_code = {c.code: c.id for c in customers}
    sup_by_code = {s.code: s.id for s in suppliers}
    sup_by_name = {s.name.lower(): s.id for s in suppliers}
    default_bank = banks[0].id if banks else None

    inv_nos = {i.invoiceNumber for i in await db.salesinvoice.find_many(where={"companyId": company_id})}
    bill_nos = {b.billNumber for b in await db.supplierbill.find_many(where={"companyId": company_id})}
    rcpt_nos = {r.receiptNumber for r in await db.salesreceipt.find_many(where={"companyId": company_id})}
    pay_nos = {p.voucherNumber for p in await db.supplierpayment.find_many(where={"companyId": company_id})}
    credit_nos = {c.creditNumber for c in await db.salescredit.find_many(where={"companyId": company_id})}

    return {
        "cust_by_code": cust_by_code,
        "sup_by_code": sup_by_code,
        "sup_by_name": sup_by_name,
        "default_bank": default_bank,
        "inv_nos": inv_nos,
        "bill_nos": bill_nos,
        "rcpt_nos": rcpt_nos,
        "pay_nos": pay_nos,
        "credit_nos": credit_nos,
    }


def resolve_customer(cache: dict[str, Any], party_key: str, contact: str) -> str | None:
    if party_key in cache["cust_by_code"]:
        return cache["cust_by_code"][party_key]
    return None


def resolve_supplier(cache: dict[str, Any], party_key: str) -> str | None:
    if party_key in cache["sup_by_code"]:
        return cache["sup_by_code"][party_key]
    return cache["sup_by_name"].get(party_key.lower())


async def migrate_sales_all(
    db: Prisma, company_id: str, records: list[dict], cache: dict[str, Any]
) -> dict[str, int]:
    stats = {"invoices": 0, "receipts": 0, "credits": 0, "skipped": 0, "errors": 0}

    for i, raw in enumerate(records):
        row = normalize_row(raw)
        if not row or not row["doc_no"] or row["amount"] <= 0:
            stats["skipped"] += 1
            continue

        doc_type = row["doc_type"].lower()
        doc_no = row["doc_no"]

        try:
            if "invoice" in doc_type:
                if doc_no in cache["inv_nos"]:
                    stats["skipped"] += 1
                    continue
                cust_id = resolve_customer(cache, row["party_key"], row["contact_name"])
                if not cust_id:
                    stats["errors"] += 1
                    continue
                await db.salesinvoice.create(
                    data={
                        "companyId": company_id,
                        "invoiceNumber": doc_no,
                        "invoiceDate": parse_date(row["date"]),
                        "customerId": cust_id,
                        "totalAmount": row["amount"],
                        "status": "posted",
                        "lines": {
                            "create": [{
                                "quantity": Decimal(1),
                                "rate": row["amount"],
                                "lineSubtotal": row["amount"],
                                "lineTotal": row["amount"],
                            }],
                        },
                    },
                )
                cache["inv_nos"].add(doc_no)
                stats["invoices"] += 1

            elif "receipt" in doc_type:
                if doc_no in cache["rcpt_nos"]:
                    stats["skipped"] += 1
                    continue
                cust_id = resolve_customer(cache, row["party_key"], row["contact_name"])
                if not cust_id or not cache["default_bank"]:
                    stats["errors"] += 1
                    continue
                await db.salesreceipt.create(
                    data={
                        "companyId": company_id,
                        "receiptNumber": doc_no,
                        "receiptDate": parse_date(row["date"]),
                        "customerId": cust_id,
                        "bankAccountId": cache["default_bank"],
                        "totalAmount": row["amount"],
                        "status": "posted",
                    },
                )
                cache["rcpt_nos"].add(doc_no)
                stats["receipts"] += 1

            elif "credit" in doc_type:
                if doc_no in cache["credit_nos"]:
                    stats["skipped"] += 1
                    continue
                cust_id = resolve_customer(cache, row["party_key"], row["contact_name"])
                if not cust_id:
                    stats["errors"] += 1
                    continue
                await db.salescredit.create(
                    data={
                        "companyId": company_id,
                        "creditNumber": doc_no,
                        "creditDate": parse_date(row["date"]),
                        "customerId": cust_id,
                        "totalAmount": row["amount"],
                        "status": "posted",
                        "lines": {
                            "create": [{
                                "quantity": Decimal(1),
                                "rate": row["amount"],
                                "lineSubtotal": row["amount"],
                                "lineTotal": row["amount"],
                            }],
                        },
                    },
                )
                cache["credit_nos"].add(doc_no)
                stats["credits"] += 1
            else:
                stats["skipped"] += 1
        except Exception:
            stats["errors"] += 1

        if (i + 1) % 500 == 0:
            log(f"  sales_all: {i + 1}/{len(records)} inv+{stats['invoices']} rcpt+{stats['receipts']}")

    return stats


async def migrate_purchases_all(
    db: Prisma, company_id: str, records: list[dict], cache: dict[str, Any]
) -> dict[str, int]:
    stats = {"bills": 0, "payments": 0, "skipped": 0, "errors": 0}

    for i, raw in enumerate(records):
        row = normalize_row(raw)
        if not row or not row["doc_no"] or row["amount"] <= 0:
            stats["skipped"] += 1
            continue

        doc_type = row["doc_type"].lower()
        doc_no = row["doc_no"]

        try:
            if "invoice" in doc_type or "bill" in doc_type:
                if doc_no in cache["bill_nos"]:
                    stats["skipped"] += 1
                    continue
                sup_id = resolve_supplier(cache, row["party_key"])
                if not sup_id:
                    # party_key may be supplier name in col_2 format
                    sup_id = resolve_supplier(cache, row["contact_name"] or row["party_key"])
                if not sup_id:
                    stats["errors"] += 1
                    continue
                await db.supplierbill.create(
                    data={
                        "companyId": company_id,
                        "billNumber": doc_no,
                        "billDate": parse_date(row["date"]),
                        "supplierId": sup_id,
                        "totalAmount": row["amount"],
                        "status": "posted",
                        "lines": {
                            "create": [{
                                "quantity": Decimal(1),
                                "rate": row["amount"],
                                "lineSubtotal": row["amount"],
                                "lineTotal": row["amount"],
                            }],
                        },
                    },
                )
                cache["bill_nos"].add(doc_no)
                stats["bills"] += 1

            elif "payment" in doc_type:
                if doc_no in cache["pay_nos"]:
                    stats["skipped"] += 1
                    continue
                sup_id = resolve_supplier(cache, row["party_key"])
                if not sup_id or not cache["default_bank"]:
                    stats["errors"] += 1
                    continue
                await db.supplierpayment.create(
                    data={
                        "companyId": company_id,
                        "voucherNumber": doc_no,
                        "paymentDate": parse_date(row["date"]),
                        "supplierId": sup_id,
                        "bankAccountId": cache["default_bank"],
                        "totalAmount": row["amount"],
                        "status": "posted",
                    },
                )
                cache["pay_nos"].add(doc_no)
                stats["payments"] += 1
            else:
                stats["skipped"] += 1
        except Exception:
            stats["errors"] += 1

        if (i + 1) % 200 == 0:
            log(f"  purchases_all: {i + 1}/{len(records)} bills+{stats['bills']} pay+{stats['payments']}")

    return stats


async def run(company_id: str, json_path: Path, *, sales_only: bool = False, purchases_only: bool = False) -> None:
    log(f"Loading {json_path.name}...")
    data = json.loads(json_path.read_text(encoding="utf-8"))
    if "sections" in data:
        modules = {
            s["moduleKey"]: {"records": s.get("records", [])}
            for s in data["sections"]
        }
    else:
        modules = data.get("modules", {})

    db = Prisma()
    for attempt in range(5):
        try:
            await db.connect()
            break
        except Exception as exc:
            if attempt == 4:
                raise
            log(f"DB connect retry {attempt + 1}/5: {exc}")
            await asyncio.sleep(5 * (attempt + 1))
    cache = await preload(db, company_id)

    if not purchases_only:
        log("[1/2] Sales All (invoices + receipts + credits)...")
        sa = modules.get("sales_all", {}).get("records", [])
        log(f"  sales_all rows to process: {len(sa)}")
        sa_stats = await migrate_sales_all(db, company_id, sa, cache)
        log(f"  Sales All done: {sa_stats}")
    else:
        log("[skip] Sales All (already migrated)")

    if not sales_only:
        log("[2/2] Purchases All (bills + supplier payments)...")
        pa = modules.get("purchases_all", {}).get("records", [])
        log(f"  purchases_all rows to process: {len(pa)}")
        pa_stats = await migrate_purchases_all(db, company_id, pa, cache)
        log(f"  Purchases All done: {pa_stats}")
    else:
        log("[skip] Purchases All")

    log("\n=== Final counts ===")
    for label, model in [
        ("invoices", db.salesinvoice),
        ("receipts", db.salesreceipt),
        ("sales_credits", db.salescredit),
        ("bills", db.supplierbill),
        ("supplier_payments", db.supplierpayment),
    ]:
        n = await model.count(where={"companyId": company_id})
        log(f"  {label}: {n}")

    await db.disconnect()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--company-id", default=CID)
    p.add_argument("--input", default=str(DEFAULT_JSON))
    p.add_argument("--purchases-only", action="store_true")
    p.add_argument("--sales-only", action="store_true")
    args = p.parse_args()
    asyncio.run(
        run(
            args.company_id,
            Path(args.input),
            sales_only=args.sales_only,
            purchases_only=args.purchases_only,
        )
    )


if __name__ == "__main__":
    main()
