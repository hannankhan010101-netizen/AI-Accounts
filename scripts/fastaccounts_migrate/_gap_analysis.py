#!/usr/bin/env python3
"""Deep gap analysis: export sections vs migration coverage."""
from __future__ import annotations

import asyncio
import json
import sys
from collections import Counter
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

DEFAULT_JSON = (
    MIGRATE_DIR.parent / "fastaccounts_export" / "output" / "fastaccounts_labeled_data.json"
)
CID = "cmpfl1itj000hqubj7rne8q5f"

# Sections migrate_all.py handles
MIGRATE_ALL_KEYS = {
    "settings_coa",
    "customers",
    "suppliers",
    "products",
    "bank_account_balances",
    "sales_invoices",
    "purchase_bills",
    "sales_receipts",
    "bank_payments",
    "settings_journals",
}

# Sections migrate_aggregate.py handles
MIGRATE_AGGREGATE_KEYS = {"sales_all", "purchases_all"}

# DB entity mapping for reconciliation
DB_ENTITY_MAP = {
    "customers": ("customer", None),
    "suppliers": ("supplier", None),
    "products": ("product", None),
    "bank_account_balances": ("bankaccount", None),
    "settings_coa": ("nominalaccount", "via_section"),
    "sales_invoices": ("salesinvoice", "invoiceNumber"),
    "purchase_bills": ("supplierbill", "billNumber"),
    "sales_receipts": ("salesreceipt", "receiptNumber"),
    "bank_payments": ("bankpayment", "voucherNumber"),
    "settings_journals": ("journal", "journalNumber"),
    "sales_all": ("salesinvoice+salesreceipt+salescredit", "aggregate"),
    "purchases_all": ("supplierbill+supplierpayment+suppliercredit", "aggregate"),
    "purchase_payments": ("supplierpayment", "listing"),
}


def load_sections(path: Path) -> dict[str, list]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {s["moduleKey"]: s["records"] for s in data["sections"]}


async def db_full_counts(db: Prisma, company_id: str) -> dict[str, int]:
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
        "sales_credits": await db.salescredit.count(where={"companyId": company_id}),
        "supplier_credits": await db.suppliercredit.count(where={"companyId": company_id}),
        "supplier_payments": await db.supplierpayment.count(where={"companyId": company_id}),
        "bank_payments": await db.bankpayment.count(where={"companyId": company_id}),
        "journals": await db.journal.count(where={"companyId": company_id}),
        "quotations": await db.quotation.count(where={"companyId": company_id}),
        "sales_orders": await db.salesorder.count(where={"companyId": company_id}),
        "purchase_orders": await db.purchaseorder.count(where={"companyId": company_id}),
        "pdc_received": await db.postdatedchequereceived.count(where={"companyId": company_id}),
        "pdc_issued": await db.postdatedchequeissued.count(where={"companyId": company_id}),
        "delivery_notes": await db.deliverynote.count(where={"companyId": company_id}),
        "grn": await db.goodsreceiptnote.count(where={"companyId": company_id}),
        "stock_adjustments": await db.stockadjustment.count(where={"companyId": company_id}),
        "stock_transfers": await db.stocktransfer.count(where={"companyId": company_id}),
    }
    try:
        counts["budgets"] = await db.budget.count(where={"companyId": company_id})
    except Exception:
        counts["budgets"] = -1  # table not migrated yet
    return counts


def analyze_doc_types(records: list[dict]) -> Counter:
    types: Counter = Counter()
    for r in records:
        row = normalize_row(r)
        if row:
            types[row["doc_type"]] += 1
        else:
            types["<unparsed>"] += 1
    return types


def is_placeholder_section(records: list[dict]) -> bool:
    if not records:
        return True
    if len(records) == 1 and "Cells" in records[0]:
        return True
    return False


async def main() -> None:
    sections = load_sections(DEFAULT_JSON)
    db = Prisma()
    await db.connect()
    db_counts = await db_full_counts(db, CID)
    await db.disconnect()

    print("=== Migration gap analysis (Nafy-Pharma) ===\n")

    print("1. Export sections vs migration script coverage\n")
    for key in sorted(sections.keys()):
        recs = sections[key]
        n = len(recs)
        if key in MIGRATE_ALL_KEYS:
            handler = "migrate_all.py"
        elif key in MIGRATE_AGGREGATE_KEYS:
            handler = "migrate_aggregate.py"
        elif is_placeholder_section(recs):
            handler = "EMPTY/placeholder (no FA data)"
        else:
            handler = "NOT MIGRATED"
        print(f"  {key:30} {n:6}  -> {handler}")

    print("\n2. Transactional doc types in aggregate sections\n")
    for key in ("sales_all", "purchases_all"):
        types = analyze_doc_types(sections.get(key, []))
        print(f"  {key}:")
        for t, c in types.most_common(15):
            print(f"    {t}: {c}")

    print("\n3. Listing modules potentially overlapping aggregate\n")
    pp = sections.get("purchase_payments", [])
    if pp:
        nos = {str(r.get("Invoice No") or r.get("ID") or "").strip() for r in pp}
        nos.discard("")
        print(f"  purchase_payments: {len(pp)} rows, {len(nos)} unique doc nos")
        print(f"    sample keys: {list(pp[0].keys())[:10]}")

    print("\n4. DB counts (full entity scan)\n")
    for k, v in db_counts.items():
        print(f"  {k}: {v}")

    print("\n5. Known intentional gaps / data quality notes\n")
    notes = [
        ("Document line detail", "All invoices/bills imported as single summary line (qty=1, rate=total). Product-level lines NOT migrated."),
        ("Opening balances", "Customer/Supplier Balance field exported but NOT written to DB opening balance fields."),
        ("Product stock qty", "Product Quantity/Low Stock Level exported but NOT migrated to inventory quantities."),
        ("GST/tax lines", "Tax breakdown on invoice lines NOT migrated."),
        ("Journal GL detail", "Only 2 journals in export; migrated with placeholder nominals 310101/230901, not real lines."),
        ("Settings config", "Smart settings (29), taxes (20), business info, lock date — exported but NOT migrated to AppSettings."),
        ("Bank receipts module", "Separate from sales receipts; export has placeholder only (1 Cells row)."),
        ("Bank transfers/reconciliation", "Export placeholders only — no transactional data in FA export."),
        ("PDC / PO / stock adj", "Export placeholders only (1 row each) — nothing to migrate for Nafy-Pharma."),
        ("sales_orders (17200)", "Duplicate grid of sales_all activity lines — covered by migrate_aggregate sales_all."),
        ("Supplier credits", "Check purchases_all for credit doc types — see section 2 above."),
        ("Budgets", "Not in FastAccounts export — new AI-Accounts module only."),
    ]
    for title, detail in notes:
        print(f"  • {title}: {detail}")

    # Check supplier credits in purchases_all
    credit_rows = [
        normalize_row(r)
        for r in sections.get("purchases_all", [])
        if normalize_row(r) and "credit" in normalize_row(r)["doc_type"].lower()
    ]
    print(f"\n6. Supplier credits in export: {len(credit_rows)} rows")
    print(f"   Supplier credits in DB: {db_counts['supplier_credits']}")

    # Check invoices with journalId (posted to GL)
    db2 = Prisma()
    await db2.connect()
    posted_inv = await db2.salesinvoice.count(
        where={"companyId": CID, "journalId": {"not": None}}
    )
    draft_inv = await db2.salesinvoice.count(where={"companyId": CID, "status": "draft"})
    posted_bill = await db2.supplierbill.count(
        where={"companyId": CID, "journalId": {"not": None}}
    )
    inv_with_product = await db2.salesinvoiceline.count(
        where={
            "salesInvoice": {"is": {"companyId": CID}},
            "productCode": {"not": None},
        }
    )
    await db2.disconnect()

    print("\n7. Posting / line quality in DB\n")
    print(f"  Invoices with journalId (GL posted): {posted_inv}/{db_counts['invoices']}")
    print(f"  Invoices still draft: {draft_inv}")
    print(f"  Bills with journalId: {posted_bill}/{db_counts['bills']}")
    print(f"  Invoice lines with productCode: {inv_with_product} (expect 0 if summary-only migration)")


if __name__ == "__main__":
    asyncio.run(main())
