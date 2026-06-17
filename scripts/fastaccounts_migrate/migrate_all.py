#!/usr/bin/env python3
"""FastAccounts → AI-Accounts bulk migration (optimized, read-only source)."""
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

CATEGORY_TYPE_MAP = {
    "capital & reserves": "Equity",
    "fixed assets": "Asset",
    "current assets": "Asset",
    "current liabilities": "Liability",
    "long term liabilities": "Liability",
    "sales": "Income",
    "cost of sales": "Expense",
    "overheads": "Expense",
    "expenses": "Expense",
    "income": "Income",
}


def log(msg: str) -> None:
    print(msg, flush=True)


class Stats:
    def __init__(self) -> None:
        self.counts: dict[str, dict[str, int]] = {}

    def add(self, module: str, key: str, n: int = 1) -> None:
        self.counts.setdefault(module, {}).setdefault(key, 0)
        self.counts[module][key] += n

    def report(self) -> None:
        log("\n=== Migration summary ===")
        for mod, parts in self.counts.items():
            log(f"  {mod}: {parts}")


def slug_code(name: str, max_len: int = 20) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "_", name.strip().lower()).strip("_")
    return (s or "misc")[:max_len]


def parse_decimal(val: Any) -> Decimal:
    if val is None:
        return Decimal(0)
    s = str(val).replace(",", "").strip()
    if not s:
        return Decimal(0)
    try:
        return Decimal(s)
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


def load_sections(path: Path) -> dict[str, list[dict[str, Any]]]:
    log(f"Loading {path.name}...")
    data = json.loads(path.read_text(encoding="utf-8"))
    sections = {s["moduleKey"]: s["records"] for s in data.get("sections", [])}
    log(f"Loaded {len(sections)} sections")
    return sections


async def preload(db: Prisma, company_id: str) -> dict[str, Any]:
    log("Preloading existing records...")
    customers = await db.customer.find_many(where={"companyId": company_id})
    suppliers = await db.supplier.find_many(where={"companyId": company_id})
    products = await db.product.find_many(where={"companyId": company_id})
    banks = await db.bankaccount.find_many(where={"companyId": company_id})
    nominals = await db.nominalaccount.find_many(
        where={"section": {"is": {"category": {"is": {"companyId": company_id}}}}},
    )
    categories = await db.coacategory.find_many(where={"companyId": company_id})
    sections = await db.coasection.find_many(
        where={"category": {"is": {"companyId": company_id}}},
        include={"category": True},
    )

    cust_by_code = {c.code: c.id for c in customers}
    sup_by_code = {s.code: s.id for s in suppliers}
    prod_by_code = {p.code: p.id for p in products}
    bank_by_name = {b.name.lower(): b.id for b in banks}
    nominal_by_code = {n.code: n.id for n in nominals}
    nominal_by_name = {n.name.lower(): n.code for n in nominals}
    cat_by_name = {c.name.lower(): c.id for c in categories}
    sec_by_key = {(s.categoryId, s.name.lower()): s.id for s in sections}

    return {
        "cust_by_code": cust_by_code,
        "sup_by_code": sup_by_code,
        "prod_by_code": prod_by_code,
        "bank_by_name": bank_by_name,
        "nominal_by_code": nominal_by_code,
        "nominal_by_name": nominal_by_name,
        "cat_by_name": cat_by_name,
        "sec_by_key": sec_by_key,
    }


async def migrate_coa(
    db: Prisma, company_id: str, records: list[dict], cache: dict[str, Any], stats: Stats
) -> None:
    for i, r in enumerate(records):
        code = str(r.get("1") or "").strip()
        name = str(r.get("2") or "").strip()
        section_name = str(r.get("3") or "General").strip()
        category_name = str(r.get("4") or "Other").strip()
        if not code or not name:
            stats.add("coa", "skipped")
            continue
        if code in cache["nominal_by_code"]:
            stats.add("coa", "skipped")
            continue

        cat_key = category_name.lower()
        cat_id = cache["cat_by_name"].get(cat_key)
        if not cat_id:
            row = await db.coacategory.create(
                data={
                    "companyId": company_id,
                    "code": slug_code(category_name),
                    "name": category_name,
                    "categoryType": CATEGORY_TYPE_MAP.get(cat_key, "Other"),
                },
            )
            cat_id = row.id
            cache["cat_by_name"][cat_key] = cat_id

        sec_key = (cat_id, section_name.lower())
        sec_id = cache["sec_by_key"].get(sec_key)
        if not sec_id:
            row = await db.coasection.create(
                data={"categoryId": cat_id, "code": slug_code(section_name), "name": section_name},
            )
            sec_id = row.id
            cache["sec_by_key"][sec_key] = sec_id

        nominal = await db.nominalaccount.create(
            data={"sectionId": sec_id, "code": code, "name": name},
        )
        cache["nominal_by_code"][code] = nominal.id
        cache["nominal_by_name"][name.lower()] = code
        stats.add("coa", "created")
        if (i + 1) % 50 == 0:
            log(f"  COA: {i + 1}/{len(records)}")


async def migrate_parties(
    db: Prisma,
    company_id: str,
    records: list[dict],
    *,
    kind: str,
    cache: dict[str, Any],
    stats: Stats,
) -> None:
    code_map = cache["cust_by_code"] if kind == "customer" else cache["sup_by_code"]
    for i, r in enumerate(records):
        code = str(r.get("Account No") or "").strip()
        name = str(r.get("Business Name") or r.get("Contact Name") or "").strip()
        if not code or not name:
            stats.add(kind + "s", "skipped")
            continue
        if code in code_map:
            stats.add(kind + "s", "skipped")
            continue
        email = str(r.get("Email") or "").strip() or None
        phone = str(r.get("Mobile") or "").strip() or None
        if kind == "customer":
            row = await db.customer.create(
                data={"companyId": company_id, "code": code, "name": name, "email": email, "phone": phone},
            )
        else:
            row = await db.supplier.create(
                data={"companyId": company_id, "code": code, "name": name, "email": email, "phone": phone},
            )
        code_map[code] = row.id
        stats.add(kind + "s", "created")
        if (i + 1) % 50 == 0:
            log(f"  {kind}s: {i + 1}/{len(records)}")


async def migrate_products(
    db: Prisma, company_id: str, records: list[dict], cache: dict[str, Any], stats: Stats
) -> None:
    code_map = cache["prod_by_code"]
    for i, r in enumerate(records):
        code = str(r.get("Code") or r.get("ID") or "").strip()
        name = str(r.get("Product Name") or "").strip()
        if not code or not name:
            stats.add("products", "skipped")
            continue
        if code in code_map:
            stats.add("products", "skipped")
            continue
        row = await db.product.create(
            data={
                "companyId": company_id,
                "code": code,
                "name": name,
                "category": str(r.get("Category") or "").strip() or None,
                "salePrice": parse_decimal(r.get("Sale Price")),
                "cost": Decimal(0),
                "isStock": True,
            },
        )
        code_map[code] = row.id
        stats.add("products", "created")
        if (i + 1) % 100 == 0:
            log(f"  products: {i + 1}/{len(records)}")


async def migrate_bank_accounts(
    db: Prisma, company_id: str, records: list[dict], cache: dict[str, Any], stats: Stats
) -> None:
    name_map = cache["bank_by_name"]
    for r in records:
        name = str(r.get("Col 0") or "").strip()
        if not name:
            stats.add("bank_accounts", "skipped")
            continue
        key = name.lower()
        if key in name_map:
            stats.add("bank_accounts", "skipped")
            continue
        row = await db.bankaccount.create(
            data={
                "companyId": company_id,
                "name": name,
                "nominalCode": str(r.get("Col 1") or "").strip() or None,
                "currency": str(r.get("Col 3") or "PKR").strip() or "PKR",
            },
        )
        name_map[key] = row.id
        stats.add("bank_accounts", "created")


async def migrate_sales_invoices(
    db: Prisma, company_id: str, records: list[dict], cache: dict[str, Any], stats: Stats
) -> None:
    existing = {
        r.invoiceNumber
        for r in await db.salesinvoice.find_many(where={"companyId": company_id})
    }
    cust = cache["cust_by_code"]
    for r in records:
        inv_no = str(r.get("Invoice No") or r.get("ID") or "").strip()
        acct = str(r.get("Account No") or "").strip()
        if not inv_no or not acct or inv_no in existing:
            stats.add("invoices", "skipped")
            continue
        cust_id = cust.get(acct)
        if not cust_id:
            stats.add("invoices", "missing_customer")
            continue
        total = parse_decimal(r.get("Total"))
        status = "posted" if "paid" in str(r.get("Invoice Status") or "").lower() else "draft"
        await db.salesinvoice.create(
            data={
                "companyId": company_id,
                "invoiceNumber": inv_no,
                "invoiceDate": parse_date(r.get("Invoice Date")),
                "customerId": cust_id,
                "totalAmount": total,
                "status": status,
                "lines": {"create": [{"quantity": Decimal(1), "rate": total, "lineSubtotal": total, "lineTotal": total}]},
            },
        )
        existing.add(inv_no)
        stats.add("invoices", "created")


async def migrate_supplier_bills(
    db: Prisma, company_id: str, records: list[dict], cache: dict[str, Any], stats: Stats
) -> None:
    existing = {
        r.billNumber
        for r in await db.supplierbill.find_many(where={"companyId": company_id})
    }
    sup = cache["sup_by_code"]
    for r in records:
        bill_no = str(r.get("Invoice No") or r.get("ID") or "").strip()
        acct = str(r.get("Account No") or "").strip()
        if not bill_no or not acct or bill_no in existing:
            stats.add("bills", "skipped")
            continue
        sup_id = sup.get(acct)
        if not sup_id:
            stats.add("bills", "missing_supplier")
            continue
        total = parse_decimal(r.get("Total"))
        status = "posted" if "paid" in str(r.get("Invoice Status") or "").lower() else "draft"
        await db.supplierbill.create(
            data={
                "companyId": company_id,
                "billNumber": bill_no,
                "billDate": parse_date(r.get("Invoice Date")),
                "supplierId": sup_id,
                "totalAmount": total,
                "status": status,
                "lines": {"create": [{"quantity": Decimal(1), "rate": total, "lineSubtotal": total, "lineTotal": total}]},
            },
        )
        existing.add(bill_no)
        stats.add("bills", "created")


async def migrate_purchase_payments_listing(
    db: Prisma, company_id: str, records: list[dict], cache: dict[str, Any], stats: Stats
) -> None:
    """Import bills surfaced only on FA Purchases → Payments grid (Type=Bill)."""

    existing = {
        r.billNumber
        for r in await db.supplierbill.find_many(where={"companyId": company_id})
    }
    sup = cache["sup_by_code"]
    for r in records:
        if str(r.get("Type") or "").strip().lower() != "bill":
            stats.add("purchase_payments_listing", "skipped_non_bill")
            continue
        bill_no = str(r.get("Invoice No") or r.get("ID") or "").strip()
        acct = str(r.get("Account No") or "").strip()
        if not bill_no or not acct or bill_no in existing:
            stats.add("purchase_payments_listing", "skipped")
            continue
        sup_id = sup.get(acct)
        if not sup_id:
            stats.add("purchase_payments_listing", "missing_supplier")
            continue
        total = parse_decimal(r.get("Total"))
        status = "posted" if "paid" in str(r.get("Invoice Status") or "").lower() else "draft"
        await db.supplierbill.create(
            data={
                "companyId": company_id,
                "billNumber": bill_no,
                "billDate": parse_date(r.get("Invoice Date")),
                "supplierId": sup_id,
                "totalAmount": total,
                "status": status,
                "lines": {"create": [{"quantity": Decimal(1), "rate": total, "lineSubtotal": total, "lineTotal": total}]},
            },
        )
        existing.add(bill_no)
        stats.add("purchase_payments_listing", "created")


async def migrate_sales_receipts(
    db: Prisma, company_id: str, records: list[dict], cache: dict[str, Any], stats: Stats
) -> None:
    existing = {
        r.receiptNumber
        for r in await db.salesreceipt.find_many(where={"companyId": company_id})
    }
    default_bank = next(iter(cache["bank_by_name"].values()), None)
    if not default_bank:
        stats.add("receipts", "no_bank")
        return
    cust = cache["cust_by_code"]
    for r in records:
        rcpt_no = str(r.get("Voucher IDLink") or r.get("ID") or "").strip()
        acct = str(r.get("Account No") or "").strip()
        if not rcpt_no or not acct or rcpt_no in existing:
            stats.add("receipts", "skipped")
            continue
        cust_id = cust.get(acct)
        if not cust_id:
            stats.add("receipts", "missing_customer")
            continue
        await db.salesreceipt.create(
            data={
                "companyId": company_id,
                "receiptNumber": rcpt_no,
                "receiptDate": parse_date(r.get("Payment Date")),
                "customerId": cust_id,
                "bankAccountId": default_bank,
                "totalAmount": parse_decimal(r.get("Amount") or r.get("Total")),
                "status": "posted",
            },
        )
        existing.add(rcpt_no)
        stats.add("receipts", "created")


async def migrate_bank_payments(
    db: Prisma, company_id: str, records: list[dict], cache: dict[str, Any], stats: Stats
) -> None:
    existing_rows = await db.bankpayment.find_many(where={"companyId": company_id})
    seen: set[str] = {
        f"{r.voucherNumber}|{r.nominalCode or ''}|{r.totalAmount}"
        for r in existing_rows
    }
    banks = cache["bank_by_name"]
    nom_names = cache["nominal_by_name"]
    default_bank = next(iter(banks.values()), None)

    for i, r in enumerate(records):
        voucher = str(r.get("Voucher IDLink") or r.get("ID") or "").strip()
        bank_name = str(r.get("Bank Name") or "").strip().lower()
        account_name = str(r.get("Account") or "").strip()
        amount = parse_decimal(r.get("Bank Amount"))
        if not voucher or amount <= 0:
            stats.add("bank_payments", "skipped")
            continue
        dedupe = f"{voucher}|{account_name}|{amount}"
        nominal_code = nom_names.get(account_name.lower())
        existing_key = f"{voucher}|{nominal_code or ''}|{amount}"
        if dedupe in seen or existing_key in seen:
            stats.add("bank_payments", "duplicate_line")
            continue
        seen.add(dedupe)
        seen.add(existing_key)

        bank_id = banks.get(bank_name) or default_bank
        if not bank_id:
            stats.add("bank_payments", "no_bank")
            continue

        await db.bankpayment.create(
            data={
                "companyId": company_id,
                "voucherNumber": voucher,
                "paymentDate": parse_date(r.get("Payment Date")),
                "bankAccountId": bank_id,
                "nominalCode": nominal_code,
                "totalAmount": amount,
                "status": "posted",
            },
        )
        stats.add("bank_payments", "created")
        if (i + 1) % 200 == 0:
            log(f"  bank_payments: {i + 1}/{len(records)}")


async def migrate_journals(
    db: Prisma, company_id: str, records: list[dict], stats: Stats
) -> None:
    existing = {
        r.journalNumber
        for r in await db.journal.find_many(where={"companyId": company_id})
    }
    for r in records:
        jno = str(r.get("Col 1") or r.get("Col 2") or "").strip()
        amount = parse_decimal(r.get("Col 5"))
        if not jno or amount <= 0 or jno in existing:
            stats.add("journals", "skipped")
            continue
        await db.journal.create(
            data={
                "companyId": company_id,
                "journalNumber": jno,
                "journalDate": parse_date(r.get("Col 3")),
                "refNo": str(r.get("Col 4") or "").strip() or None,
                "totalAmount": amount,
                "status": "posted",
                "sourceType": "FASTACCOUNTS_MIGRATION",
                "lines": {
                    "create": [
                        {"nominalCode": "310101", "debit": amount, "credit": Decimal(0)},
                        {"nominalCode": "230901", "debit": Decimal(0), "credit": amount},
                    ],
                },
            },
        )
        existing.add(jno)
        stats.add("journals", "created")


async def run_migration(company_id: str, json_path: Path) -> None:
    sections = load_sections(json_path)
    stats = Stats()
    db = Prisma()
    await db.connect()

    company = await db.company.find_unique(where={"id": company_id})
    if not company:
        raise SystemExit(f"Company not found: {company_id}")
    log(f"Migrating into: {company.name} ({company_id})")

    cache = await preload(db, company_id)

    log("[1/9] Chart of accounts...")
    await migrate_coa(db, company_id, sections.get("settings_coa", []), cache, stats)

    log("[2/9] Customers...")
    await migrate_parties(db, company_id, sections.get("customers", []), kind="customer", cache=cache, stats=stats)

    log("[3/9] Suppliers...")
    await migrate_parties(db, company_id, sections.get("suppliers", []), kind="supplier", cache=cache, stats=stats)

    log("[4/9] Products...")
    await migrate_products(db, company_id, sections.get("products", []), cache, stats)

    log("[5/9] Bank accounts...")
    await migrate_bank_accounts(db, company_id, sections.get("bank_account_balances", []), cache, stats)

    log("[6/9] Sales invoices...")
    await migrate_sales_invoices(db, company_id, sections.get("sales_invoices", []), cache, stats)

    log("[7/9] Supplier bills...")
    await migrate_supplier_bills(db, company_id, sections.get("purchase_bills", []), cache, stats)

    log("[7b] Purchase payments listing (orphan bills)...")
    await migrate_purchase_payments_listing(
        db, company_id, sections.get("purchase_payments", []), cache, stats
    )

    log("[8/9] Sales receipts...")
    await migrate_sales_receipts(db, company_id, sections.get("sales_receipts", []), cache, stats)

    log("[9/9] Bank payments...")
    await migrate_bank_payments(db, company_id, sections.get("bank_payments", []), cache, stats)

    log("[+] Journals...")
    await migrate_journals(db, company_id, sections.get("settings_journals", []), stats)

    log("\n=== Database counts ===")
    counts = {
        "customers": await db.customer.count(where={"companyId": company_id}),
        "suppliers": await db.supplier.count(where={"companyId": company_id}),
        "products": await db.product.count(where={"companyId": company_id}),
        "bank_accounts": await db.bankaccount.count(where={"companyId": company_id}),
        "nominals": await db.nominalaccount.count(
            where={"section": {"is": {"category": {"is": {"companyId": company_id}}}}}
        ),
        "invoices": await db.salesinvoice.count(where={"companyId": company_id}),
        "bills": await db.supplierbill.count(where={"companyId": company_id}),
        "receipts": await db.salesreceipt.count(where={"companyId": company_id}),
        "bank_payments": await db.bankpayment.count(where={"companyId": company_id}),
        "journals": await db.journal.count(where={"companyId": company_id}),
    }
    for k, v in counts.items():
        log(f"  {k}: {v}")

    stats.report()
    await db.disconnect()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--company-id", default="cmpfl1itj000hqubj7rne8q5f")
    p.add_argument("--input", default=str(DEFAULT_JSON))
    args = p.parse_args()
    asyncio.run(run_migration(args.company_id, Path(args.input)))


if __name__ == "__main__":
    main()
