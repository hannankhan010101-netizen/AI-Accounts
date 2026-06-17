#!/usr/bin/env python3
"""Compare FA import AR/AP balance snapshot vs live aging for migrated tenant."""
from __future__ import annotations

import asyncio
import json
import os
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "Backend"
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")
if os.getenv("DIRECT_URL"):
    os.environ["DATABASE_URL"] = os.environ["DIRECT_URL"]

from prisma_generated import Prisma
from app.services.aging_service import AgingService

MIGRATE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(MIGRATE_DIR))
from _tenant import tenant_id  # noqa: E402

CID = tenant_id()
TOLERANCE = Decimal("1.00")


def _sum_fa_balances(entries: list[dict]) -> Decimal:
    total = Decimal(0)
    for e in entries:
        try:
            total += Decimal(str(e.get("balance") or 0))
        except Exception:  # noqa: BLE001
            continue
    return total


async def main() -> None:
    db = Prisma()
    await db.connect()
    aging = AgingService(db)

    ar = await aging.ar_aging(company_id=CID, as_of_date=None)
    ap = await aging.ap_aging(company_id=CID, as_of_date=None)

    customers = await db.customer.find_many(where={"companyId": CID})
    suppliers = await db.supplier.find_many(where={"companyId": CID})
    code_by_customer = {c.id: c.code for c in customers}
    code_by_supplier = {s.id: s.code for s in suppliers}

    smart = await db.smartsettings.find_unique(where={"companyId": CID})
    payload = smart.payload if smart and isinstance(smart.payload, dict) else {}
    fa_import = payload.get("fastAccountsImport") if isinstance(payload.get("fastAccountsImport"), dict) else {}
    fa_ar = fa_import.get("customerBalances") or []
    fa_ap = fa_import.get("supplierBalances") or []
    if not isinstance(fa_ar, list):
        fa_ar = []
    if not isinstance(fa_ap, list):
        fa_ap = []

    fa_ar_by_code = {str(e.get("code", "")): Decimal(str(e.get("balance", 0))) for e in fa_ar if e.get("code")}
    fa_ap_by_code = {str(e.get("code", "")): Decimal(str(e.get("balance", 0))) for e in fa_ap if e.get("code")}

    live_ar_total = sum(Decimal(str(r.get("balance") or 0)) for r in ar.get("rows") or [])
    live_ap_total = sum(Decimal(str(r.get("balance") or 0)) for r in ap.get("rows") or [])
    fa_ar_total = _sum_fa_balances(fa_ar)
    fa_ap_total = _sum_fa_balances(fa_ap)

    ar_mismatches = 0
    for row in ar.get("rows") or []:
        pid = row.get("partyId")
        code = code_by_customer.get(pid, "")
        if not code or code not in fa_ar_by_code:
            continue
        live = Decimal(str(row.get("balance") or 0))
        snap = fa_ar_by_code[code]
        if abs(live - snap) > TOLERANCE:
            ar_mismatches += 1

    ap_mismatches = 0
    for row in ap.get("rows") or []:
        pid = row.get("partyId")
        code = code_by_supplier.get(pid, "")
        if not code or code not in fa_ap_by_code:
            continue
        live = Decimal(str(row.get("balance") or 0))
        snap = fa_ap_by_code[code]
        if abs(live - snap) > TOLERANCE:
            ap_mismatches += 1

    await db.disconnect()

    print(f"=== AR/AP spot check ({CID}) ===\n")
    print(f"  Live AR total (aging):     {live_ar_total}")
    print(f"  FA snapshot AR total:      {fa_ar_total}")
    print(f"  AR delta:                  {live_ar_total - fa_ar_total}")
    print(f"  Party-level AR mismatches: {ar_mismatches} (tolerance {TOLERANCE})")
    print()
    print(f"  Live AP total (aging):     {live_ap_total}")
    print(f"  FA snapshot AP total:      {fa_ap_total}")
    print(f"  AP delta:                  {live_ap_total - fa_ap_total}")
    print(f"  Party-level AP mismatches: {ap_mismatches}")

    ok = (
        abs(live_ar_total - fa_ar_total) <= TOLERANCE * 10
        and abs(live_ap_total - fa_ap_total) <= TOLERANCE * 10
    )
    print(
        f"\n  Totals within tolerance: "
        f"{'YES' if ok else 'REVIEW'}"
    )
    if not ok:
        print(
            "  Note: migrated data uses summary GL (6 nominals). Open-item aging"
        )
        print(
            "  totals often differ from FA party balance snapshots; use TB + doc counts for go-live."
        )
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    asyncio.run(main())
