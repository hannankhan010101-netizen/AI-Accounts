#!/usr/bin/env python3
"""Run priority reports and print row counts (parity smoke for Insights)."""
from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "Backend"
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")


def _configure_session_db_url() -> None:
    """Use session pooler (DIRECT_URL) with a single Prisma connection for sequential runs."""

    url = (os.getenv("DIRECT_URL") or os.getenv("DATABASE_URL") or "").strip()
    if not url:
        return
    if "connection_limit=" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}connection_limit=1"
    os.environ["DATABASE_URL"] = url


_configure_session_db_url()

from prisma_generated import Prisma  # noqa: E402
from app.services.report_query_service import ReportQueryService  # noqa: E402

MIGRATE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(MIGRATE_DIR))
from _tenant import tenant_id  # noqa: E402

CID = tenant_id()

# (report_id, label, optional extra criteria)
PRIORITY: list[tuple[str, str, dict]] = [
    ("203", "Trial balance", {}),
    ("204", "Profit and loss", {}),
    ("205", "Balance sheet", {}),
    ("GL", "General ledger (410101)", {
        "nominalCode": "410101",
        # Narrow window — full history can timeout on large tenants.
        "dateFrom": datetime(datetime.now(timezone.utc).year, 1, 1, tzinfo=timezone.utc).isoformat(),
    }),
    ("028", "Sale invoices by date", {}),
    ("032", "Sale summary by date", {}),
    ("048", "Purchase bills by date", {}),
    ("034", "Customer statement", {}),
    ("054", "Supplier statement", {}),
    ("047", "Customer balances summary", {}),
    ("067", "Supplier balances summary", {}),
    ("071", "Bank payments", {}),
    ("080", "Stock quantity", {}),
    ("AR_AGING", "AR aging", {}),
    ("AP_AGING", "AP aging", {}),
    ("BUDGET_VS_ACTUAL", "Budget vs actual", {}),
]

OPTIONAL_IF_EMPTY = frozenset({"BUDGET_VS_ACTUAL", "206", "STOCK_XFR"})

# Reports that need a party id — filled at runtime from first DB row.
PARTY_REPORTS: dict[str, tuple[str, str]] = {
    "034": ("customerId", "customer"),
    "054": ("supplierId", "supplier"),
}


def _default_criteria(report_id: str, extra: dict) -> dict[str, object]:
    now = datetime.now(timezone.utc)
    criteria: dict[str, object] = {
        "pageSize": 500,
        "dateFrom": datetime(2020, 1, 1, tzinfo=timezone.utc).isoformat(),
        "dateTo": now.isoformat(),
    }
    criteria.update(extra)
    return criteria


def _is_stub(rows: list[dict]) -> bool:
    if len(rows) != 1:
        return False
    msg = str(rows[0].get("message") or "")
    return "not implemented" in msg.lower()


async def _reconnect(db: Prisma) -> tuple[Prisma, ReportQueryService]:
    """Fresh Prisma client — avoids Supabase pooler exhaustion on long smoke runs."""

    from datetime import timedelta

    try:
        await db.disconnect()
    except Exception:  # noqa: BLE001
        pass
    await asyncio.sleep(0.5)
    fresh = Prisma(connect_timeout=timedelta(seconds=120))
    await fresh.connect()
    return fresh, ReportQueryService(prisma=fresh)


# Reports that benefit from a fresh DB connection before execution.
RECONNECT_BEFORE = frozenset(
    {"203", "204", "205", "GL", "047", "067", "AR_AGING", "AP_AGING"}
)
TIMEOUT_RETRYABLE = ("timeout", "readtimeout", "pool", "connection", "closed", "reset")
MAX_ATTEMPTS = 3


def _is_retryable(exc: BaseException) -> bool:
    blob = f"{exc.__class__.__name__} {exc}".lower()
    return any(token in blob for token in TIMEOUT_RETRYABLE)


async def _run_report(
    *,
    db: Prisma,
    svc: ReportQueryService,
    report_id: str,
    criteria: dict[str, object],
) -> tuple[list[dict], Prisma, ReportQueryService]:
    last_exc: BaseException | None = None
    for attempt in range(MAX_ATTEMPTS):
        if report_id in RECONNECT_BEFORE or attempt > 0:
            db, svc = await _reconnect(db)
        try:
            rows = await svc.execute(
                company_id=CID, report_id=report_id, criteria=criteria
            )
            return rows, db, svc
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if attempt + 1 < MAX_ATTEMPTS and _is_retryable(exc):
                await asyncio.sleep(1.5 * (attempt + 1))
                continue
            raise
    assert last_exc is not None
    raise last_exc


async def _resolve_party_criteria(
    db: Prisma, report_id: str, criteria: dict[str, object]
) -> dict[str, object]:
    spec = PARTY_REPORTS.get(report_id)
    if spec is None:
        return criteria
    field, kind = spec
    if criteria.get(field):
        return criteria
    if kind == "customer":
        row = await db.customer.find_first(where={"companyId": CID})
        if row:
            criteria[field] = row.id
    elif kind == "supplier":
        row = await db.supplier.find_first(where={"companyId": CID})
        if row:
            criteria[field] = row.id
    return criteria


async def main() -> int:
    from datetime import timedelta

    db = Prisma(connect_timeout=timedelta(seconds=120))
    await db.connect()
    svc = ReportQueryService(prisma=db)

    si_count = await db.salesinvoice.count(where={"companyId": CID})
    bill_count = await db.supplierbill.count(where={"companyId": CID})

    print(f"=== Report spot check ({CID}) ===\n")
    print(f"  DB sales invoices: {si_count}")
    print(f"  DB supplier bills:  {bill_count}\n")
    print(f"  {'ID':<8}  {'Rows':>6}  {'Status':<10}  Name")
    print(f"  {'-'*8}  {'-'*6}  {'-'*10}  {'-'*30}")

    failures = 0
    stubs = 0
    for report_id, label, extra in PRIORITY:
        criteria = _default_criteria(report_id, extra)
        criteria = await _resolve_party_criteria(db, report_id, criteria)
        try:
            rows, db, svc = await _run_report(
                db=db,
                svc=svc,
                report_id=report_id,
                criteria=criteria,
            )
            if _is_stub(rows):
                status = "STUB"
                stubs += 1
            elif len(rows) == 0:
                if report_id in OPTIONAL_IF_EMPTY:
                    status = "OK(empty)"
                elif rows and str(rows[0].get("message") or "").strip():
                    status = "NEEDS_CRIT"
                    failures += 1
                else:
                    status = "EMPTY"
                    failures += 1
            else:
                status = "OK"
            print(f"  {report_id:<8}  {len(rows):>6}  {status:<10}  {label}")
        except Exception as exc:  # noqa: BLE001
            detail = str(exc).strip() or exc.__class__.__name__
            print(f"  {report_id:<8}  {'—':>6}  ERROR      {label}: {detail}")
            failures += 1
        await asyncio.sleep(0.2)

    await db.disconnect()

    print()
    if failures:
        print(f"  REPORT CHECK: REVIEW ({failures} empty/error)")
        return 1
    if stubs:
        print(f"  REPORT CHECK: REVIEW ({stubs} stub handlers)")
        return 1
    print("  REPORT CHECK: PASS (priority reports return rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
