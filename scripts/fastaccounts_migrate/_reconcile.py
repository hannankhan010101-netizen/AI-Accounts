#!/usr/bin/env python3
"""Compare FastAccounts export vs AI-Accounts DB for Nafy-Pharma migration."""
from __future__ import annotations

import asyncio
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "Backend"
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

import os

if os.getenv("DIRECT_URL"):
    os.environ["DATABASE_URL"] = os.environ["DIRECT_URL"]

from prisma_generated import Prisma

# Reuse row normalizer from aggregate migrator.
MIGRATE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(MIGRATE_DIR))
from _tenant import tenant_id  # noqa: E402
from migrate_aggregate import normalize_row, parse_decimal  # noqa: E402

DEFAULT_JSON = (
    Path(__file__).resolve().parents[1]
    / "fastaccounts_export"
    / "output"
    / "fastaccounts_labeled_data.json"
)
CID = tenant_id()  # HAK — migrated Nafy-Pharma data (override via GO_LIVE_COMPANY_ID)

MASTER_KEYS = {
    "customers": "customers",
    "suppliers": "suppliers",
    "products": "products",
    "bank_account_balances": "bank_accounts",
    "settings_coa": "nominals",
    "bank_payments": "bank_payments",
    "settings_journals": "journals",
}


def load_sections(path: Path) -> dict[str, list]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {s["moduleKey"]: s["records"] for s in data["sections"]}


def classify_sales(doc_type: str) -> str | None:
    lower = doc_type.lower()
    if "invoice" in lower:
        return "invoices"
    if "receipt" in lower:
        return "receipts"
    if "credit" in lower:
        return "credits"
    return None


def classify_purchase(doc_type: str) -> str | None:
    lower = doc_type.lower()
    if "invoice" in lower or "bill" in lower:
        return "bills"
    if "payment" in lower:
        return "payments"
    return None


def module_doc_no(record: dict, *fields: str) -> str:
    for f in fields:
        v = str(record.get(f) or "").strip()
        if v:
            return v
    return ""


def aggregate_unique_docs(records: list[dict], classifier) -> dict[str, set[str]]:
    buckets: dict[str, set[str]] = defaultdict(set)
    skipped = 0
    for raw in records:
        row = normalize_row(raw)
        if not row or not row["doc_no"] or row["amount"] <= 0:
            skipped += 1
            continue
        kind = classifier(row["doc_type"])
        if kind:
            buckets[kind].add(row["doc_no"])
        else:
            skipped += 1
    buckets["_skipped_rows"] = {str(skipped)}  # type: ignore[assignment]
    return buckets


def listing_unique_docs(records: list[dict], field: str, alt_field: str | None = None) -> set[str]:
    out: set[str] = set()
    for r in records:
        no = module_doc_no(r, field, alt_field or "", "ID")
        if no:
            out.add(no)
    return out


async def db_counts(db: Prisma, company_id: str) -> dict[str, int]:
    return {
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
        "credits": await db.salescredit.count(where={"companyId": company_id}),
        "payments": await db.supplierpayment.count(where={"companyId": company_id}),
        "bank_payments": await db.bankpayment.count(where={"companyId": company_id}),
        "journals": await db.journal.count(where={"companyId": company_id}),
    }


async def db_doc_sets(db: Prisma, company_id: str) -> dict[str, set[str]]:
    invs = await db.salesinvoice.find_many(where={"companyId": company_id})
    bills = await db.supplierbill.find_many(where={"companyId": company_id})
    rcpts = await db.salesreceipt.find_many(where={"companyId": company_id})
    credits = await db.salescredit.find_many(where={"companyId": company_id})
    pays = await db.supplierpayment.find_many(where={"companyId": company_id})
    return {
        "invoices": {i.invoiceNumber for i in invs},
        "bills": {b.billNumber for b in bills},
        "receipts": {r.receiptNumber for r in rcpts},
        "credits": {c.creditNumber for c in credits},
        "payments": {p.voucherNumber for p in pays},
    }


def print_row(label: str, export_n: int | str, db_n: int | str, note: str = "") -> None:
    gap = ""
    if isinstance(export_n, int) and isinstance(db_n, int):
        d = db_n - export_n
        gap = f"  ({'+' if d >= 0 else ''}{d})"
    note_s = f"  [{note}]" if note else ""
    print(f"  {label:22} export={export_n!s:>6}  db={db_n!s:>6}{gap}{note_s}")


async def main() -> int:
    sections = load_sections(DEFAULT_JSON)
    db = Prisma()
    await db.connect()
    counts = await db_counts(db, CID)
    db_sets = await db_doc_sets(db, CID)
    await db.disconnect()

    print("=== FastAccounts -> Nafy-Pharma reconciliation ===\n")

    print("Master data (record count vs DB):")
    for mod_key, db_key in MASTER_KEYS.items():
        exp = len(sections.get(mod_key, []))
        print_row(mod_key, exp, counts[db_key])

    sales_all = aggregate_unique_docs(sections.get("sales_all", []), classify_sales)
    sales_skipped = int(next(iter(sales_all.pop("_skipped_rows", {"0"}))))
    purchases_all = aggregate_unique_docs(sections.get("purchases_all", []), classify_purchase)
    purchase_skipped = int(next(iter(purchases_all.pop("_skipped_rows", {"0"}))))

    # Listing modules (subset / structured exports)
    inv_listing = listing_unique_docs(sections.get("sales_invoices", []), "Invoice No")
    bill_listing = listing_unique_docs(sections.get("purchase_bills", []), "Invoice No")
    pp_bill_listing = {
        str(r.get("Invoice No") or "").strip()
        for r in sections.get("purchase_payments", [])
        if str(r.get("Type") or "").strip().lower() == "bill"
        and str(r.get("Invoice No") or "").strip()
    }
    rcpt_listing = listing_unique_docs(
        sections.get("sales_receipts", []), "Voucher IDLink", "ID"
    )

    # Combined export unique doc numbers (aggregate + listing modules)
    export_inv = sales_all.get("invoices", set()) | inv_listing
    export_bill = purchases_all.get("bills", set()) | bill_listing | pp_bill_listing
    export_rcpt = sales_all.get("receipts", set()) | rcpt_listing
    export_credit = sales_all.get("credits", set())
    export_pay = purchases_all.get("payments", set())

    print("\nTransactional docs (unique document numbers):")
    print_row("invoices", len(export_inv), len(db_sets["invoices"]),
              "sales_all + sales_invoices")
    print_row("receipts", len(export_rcpt), len(db_sets["receipts"]),
              "sales_all + sales_receipts")
    print_row("sales_credits", len(export_credit), len(db_sets["credits"]), "sales_all only")
    print_row("bills", len(export_bill), len(db_sets["bills"]),
              "purchases_all + purchase_bills + purchase_payments (Type=Bill)")
    print_row("supplier_payments", len(export_pay), len(db_sets["payments"]), "purchases_all only")

    print("\nAggregate section row stats:")
    print(f"  sales_all rows: {len(sections.get('sales_all', []))}  "
          f"skipped/unmapped: {sales_skipped}")
    print(f"  purchases_all rows: {len(sections.get('purchases_all', []))}  "
          f"skipped/unmapped: {purchase_skipped}")
    print(f"  sales_orders rows: {len(sections.get('sales_orders', []))}  "
          f"[not imported - duplicate of sales_all]")

    missing_inv = sorted(export_inv - db_sets["invoices"])[:10]
    extra_inv = sorted(db_sets["invoices"] - export_inv)[:10]
    missing_bill = sorted(export_bill - db_sets["bills"])[:10]
    extra_bill = sorted(db_sets["bills"] - export_bill)[:10]
    missing_rcpt = sorted(export_rcpt - db_sets["receipts"])[:10]
    missing_pay = sorted(export_pay - db_sets["payments"])[:10]

    print("\nGap analysis (unique doc numbers):")
    for label, missing, extra, db_set, export_set in [
        ("invoices", missing_inv, extra_inv, db_sets["invoices"], export_inv),
        ("bills", missing_bill, extra_bill, db_sets["bills"], export_bill),
        ("receipts", missing_rcpt, [], db_sets["receipts"], export_rcpt),
        ("supplier_payments", missing_pay, [], db_sets["payments"], export_pay),
    ]:
        n_missing = len(export_set - db_set)
        n_extra = len(db_set - export_set)
        print(f"  {label}: missing_in_db={n_missing}  extra_in_db={n_extra}")
        if missing:
            print(f"    sample missing: {missing[:5]}")
        if extra:
            print(f"    sample extra: {extra[:5]}")

    print("\n=== Summary ===")
    masters_ok = all(
        len(sections.get(k, [])) == counts[v]
        for k, v in MASTER_KEYS.items()
        if k != "settings_coa"  # COA may dedupe by code
    )
    print(f"  Master data aligned: {'yes' if masters_ok else 'review COA/customers/etc'}")
    print(f"  Invoices in DB vs export unique: {len(db_sets['invoices'])}/{len(export_inv)}")
    print(f"  Bills in DB vs export unique: {len(db_sets['bills'])}/{len(export_bill)}")
    print(f"  Receipts in DB vs export unique: {len(db_sets['receipts'])}/{len(export_rcpt)}")
    print(f"  Supplier payments in DB vs export unique: "
          f"{len(db_sets['payments'])}/{len(export_pay)}")

    docs_ok = (
        len(db_sets["invoices"]) == len(export_inv)
        and len(db_sets["bills"]) == len(export_bill)
        and len(db_sets["receipts"]) == len(export_rcpt)
        and len(db_sets["payments"]) == len(export_pay)
    )
    masters_ok_go_live = all(
        len(sections.get(k, [])) == counts[v]
        for k, v in MASTER_KEYS.items()
        if k not in ("settings_coa", "settings_journals")
    )
    if docs_ok and masters_ok_go_live:
        print("\n  RECONCILE: PASS (transactional docs + masters; journals GL-expanded)")
        return 0
    if docs_ok:
        print("\n  RECONCILE: PASS docs; REVIEW masters (non-journal)")
        return 0
    print("\n  RECONCILE: FAIL (transactional doc counts differ)")
    return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
