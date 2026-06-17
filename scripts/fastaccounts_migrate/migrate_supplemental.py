#!/usr/bin/env python3
"""Backfill stock, party balances, business profile, and FA settings from export."""
from __future__ import annotations

import argparse
import asyncio
import json
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

from app.repositories.business_information_repository import BusinessInformationRepository

DEFAULT_JSON = (
    Path(__file__).resolve().parents[1]
    / "fastaccounts_export"
    / "output"
    / "fastaccounts_labeled_data.json"
)
OPENING_BATCH = "OPENING"
CID = "cmpfl1itj000hqubj7rne8q5f"


def log(msg: str) -> None:
    print(msg, flush=True)


class Stats:
    def __init__(self) -> None:
        self.counts: dict[str, dict[str, int]] = {}

    def add(self, module: str, key: str, n: int = 1) -> None:
        self.counts.setdefault(module, {}).setdefault(key, 0)
        self.counts[module][key] += n

    def report(self) -> None:
        log("\n=== Supplemental migration summary ===")
        for mod, parts in self.counts.items():
            log(f"  {mod}: {parts}")


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


def load_sections(path: Path) -> dict[str, list[dict[str, Any]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {s["moduleKey"]: s["records"] for s in data.get("sections", [])}


def form_field_map(records: list[dict]) -> dict[str, str]:
    if not records:
        return {}
    row = records[0]
    fields = row.get("Form Fields") or row.get("formFields")
    if not isinstance(fields, list):
        return {}
    out: dict[str, str] = {}
    for item in fields:
        if isinstance(item, dict):
            name = str(item.get("Name") or "").strip()
            value = str(item.get("Value") or "").strip()
            if name:
                out[name] = value
    return out


async def migrate_stock(
    db: Prisma, company_id: str, records: list[dict], stats: Stats
) -> None:
    product_codes = {
        p.code
        for p in await db.product.find_many(where={"companyId": company_id})
    }
    for r in records:
        code = str(r.get("Code") or "").strip()
        if not code or code not in product_codes:
            stats.add("stock", "skipped_unknown")
            continue
        qty = parse_decimal(r.get("Quantity"))
        low = parse_decimal(r.get("Low Stock Level"))

        if qty > 0:
            existing = await db.productbatch.find_first(
                where={
                    "companyId": company_id,
                    "productCode": code,
                    "batchNumber": OPENING_BATCH,
                }
            )
            if existing:
                if existing.quantityOnHand != qty:
                    await db.productbatch.update(
                        where={"id": existing.id},
                        data={"quantityOnHand": qty},
                    )
                    stats.add("stock", "updated_batch")
                else:
                    stats.add("stock", "skipped_batch")
            else:
                await db.productbatch.create(
                    data={
                        "companyId": company_id,
                        "productCode": code,
                        "batchNumber": OPENING_BATCH,
                        "quantityOnHand": qty,
                        "notes": "FastAccounts opening stock import",
                    }
                )
                stats.add("stock", "created_batch")


def collect_party_balances(records: list[dict]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for r in records:
        code = str(r.get("Account No") or "").strip()
        bal = parse_decimal(r.get("Balance"))
        if code and bal != 0:
            out.append({"code": code, "balance": format(bal, "f")})
    return out


def collect_supplier_balances(records: list[dict]) -> list[dict[str, str]]:
    return collect_party_balances(records)


async def migrate_business_info(
    db: Prisma, company_id: str, records: list[dict], stats: Stats
) -> None:
    fields = form_field_map(records)
    if not fields:
        stats.add("business_info", "skipped")
        return

    mapping = {
        "businessName": fields.get("company_name"),
        "addressLine1": fields.get("company_address"),
        "branchName": fields.get("company_branch_name"),
        "phoneNumber": fields.get("company_phone"),
        "mobileNumber": fields.get("company_mobile"),
        "emailAddress": fields.get("company_email"),
        "websiteAddress": fields.get("company_website"),
        "cnic": fields.get("company_cnic"),
        "stn": fields.get("company_salestax"),
        "ntn": fields.get("company_ntn"),
        "applyOnAllPrints": fields.get("chk_apply_on_all_prints") == "on",
    }
    clean = {k: v for k, v in mapping.items() if v not in (None, "")}
    if not clean:
        stats.add("business_info", "skipped")
        return

    await BusinessInformationRepository(db).upsert_fields(
        company_id=company_id, fields=clean
    )
    stats.add("business_info", "upserted")


async def migrate_smart_settings(
    db: Prisma,
    company_id: str,
    records: list[dict],
    stats: Stats,
    *,
    supplier_balances: list[dict[str, str]] | None = None,
    customer_balances: list[dict[str, str]] | None = None,
) -> None:
    if not records and not supplier_balances and not customer_balances:
        stats.add("smart_settings", "skipped")
        return

    fa_rows = [
        {
            "displayName": r.get("Display Name"),
            "label": r.get("Label"),
            "width": r.get("Width"),
            "onOff": r.get("On/Off"),
        }
        for r in records
    ]
    fa_import: dict[str, Any] = {
        "importedAt": datetime.now(timezone.utc).isoformat(),
        "smartSettingsRows": fa_rows,
    }
    if supplier_balances:
        fa_import["supplierBalances"] = supplier_balances
    if customer_balances:
        fa_import["customerBalances"] = customer_balances

    existing = await db.smartsettings.find_unique(where={"companyId": company_id})
    payload: dict[str, Any] = {"fastAccountsImport": fa_import}
    if existing and isinstance(existing.payload, dict):
        payload = {**existing.payload, **payload}

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
    stats.add("smart_settings", "upserted")


async def migrate_taxes(
    db: Prisma, company_id: str, records: list[dict], stats: Stats
) -> None:
    if not records:
        stats.add("taxes", "skipped")
        return

    fa_rows = [
        {
            "description": r.get("Description"),
            "label": r.get("Label"),
            "supplier": r.get("Supplier"),
            "customer": r.get("Customer"),
        }
        for r in records
    ]
    tax_display = json.dumps({"fastAccountsImport": fa_rows})
    await db.execute_raw(
        """
        INSERT INTO taxes_year_end_config (
            id, company_id, tax_display, gst_rates, fed_rates, adt_rates, wht_rates, tax_regions, updated_at
        )
        VALUES (
            gen_random_uuid()::text, $1, $2::jsonb, '[]'::jsonb, '[]'::jsonb,
            '[]'::jsonb, '[]'::jsonb, '[]'::jsonb, NOW()
        )
        ON CONFLICT (company_id)
        DO UPDATE SET tax_display = EXCLUDED.tax_display, updated_at = NOW()
        """,
        company_id,
        tax_display,
    )
    stats.add("taxes", "upserted")


async def run(company_id: str, json_path: Path) -> None:
    sections = load_sections(json_path)
    stats = Stats()
    db = Prisma()
    await db.connect()

    company = await db.company.find_unique(where={"id": company_id})
    if not company:
        raise SystemExit(f"Company not found: {company_id}")
    log(f"Supplemental migration for: {company.name} ({company_id})")

    log("[1/6] Opening stock batches...")
    await migrate_stock(db, company_id, sections.get("products", []), stats)

    log("[2/6] Party FA balances (stored in smart settings)...")
    customer_balances = collect_party_balances(sections.get("customers", []))
    supplier_balances = collect_supplier_balances(sections.get("suppliers", []))

    log("[3/6] Business information...")
    await migrate_business_info(db, company_id, sections.get("settings_business_info", []), stats)

    log("[4/6] Smart settings snapshot...")
    await migrate_smart_settings(
        db,
        company_id,
        sections.get("settings_smart_settings", []),
        stats,
        supplier_balances=supplier_balances,
        customer_balances=customer_balances,
    )

    log("[5/6] Taxes snapshot...")
    await migrate_taxes(db, company_id, sections.get("settings_taxes", []), stats)

    batches = await db.productbatch.count(where={"companyId": company_id})
    biz = await db.businessinformation.find_unique(where={"companyId": company_id})
    log("\n=== Verification ===")
    log(f"  product_batches: {batches}")
    log(f"  business_name: {biz.businessName if biz else '—'}")
    log(f"  customer_balances imported: {len(customer_balances)}")
    log(f"  supplier_balances imported: {len(supplier_balances)}")

    stats.report()
    await db.disconnect()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--company-id", default=CID)
    p.add_argument("--input", default=str(DEFAULT_JSON))
    args = p.parse_args()
    asyncio.run(run(args.company_id, Path(args.input)))


if __name__ == "__main__":
    main()
