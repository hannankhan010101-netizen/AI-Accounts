#!/usr/bin/env python3
"""Classify all FastAPI routes by latency SLA tier and optional live timing.

Usage:
  cd Backend
  python scripts/audit_endpoint_sla.py
  python scripts/audit_endpoint_sla.py --company-id <uuid>   # live service-layer bench

SLA tiers:
  A  Interactive read   — target p95 < 1000 ms (default page sizes)
  B  Search / list     — target p95 < 200 ms  (indexed lists, keyset pages)
  C  Excluded          — writes, exports, batch, streaming (no 1s guarantee)
"""

from __future__ import annotations

import argparse
import asyncio
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

ROUTE_DIR = SRC / "app" / "api" / "routes"

# Heuristic classification keywords in path or handler name.
TIER_C_PATTERNS = (
    r"/batch",
    r"/approve",
    r"/export",
    r"/upload",
    r"/stream",
    r"/webhook",
    r"/process-outbox",
    r"/clickhouse",
    r"/run-due",
    r"/import",
    r"/email",
    r"/post$",
    r"/void",
    r"/copy",
    r"/checkout",
    r"/portal",
)

TIER_B_PATTERNS = (
    r"/my-tasks",
    r"/audit-log",
    r"/sales-activity",
    r"/purchases-activity",
    r"/customers$",
    r"/suppliers$",
    r"/products$",
    r"keyset",
    r"/list",
    r"/peek",
)

TIER_A_REPORT = re.compile(r"/reports/")


@dataclass
class RouteInfo:
    method: str
    path: str
    handler: str
    file: str
    tier: str
    reason: str


def _tier_for(path: str, handler: str, method: str) -> tuple[str, str]:
    if method != "GET":
        return "C", "non-GET (write/action)"
    for pat in TIER_C_PATTERNS:
        if re.search(pat, path, re.I) or re.search(pat, handler, re.I):
            return "C", f"matches excluded pattern {pat!r}"
    if TIER_A_REPORT.search(path):
        return "A", "report read (1s target; cache/replica after Step 4)"
    for pat in TIER_B_PATTERNS:
        if re.search(pat, path, re.I):
            return "B", f"search/list path {pat!r}"
    if path.startswith("/health") or path.startswith("/metrics"):
        return "B", "health/metrics"
    if path.startswith("/api/v1/auth"):
        return "A", "auth (typically fast)"
    return "A", "default interactive read"


def _parse_routes() -> list[RouteInfo]:
    routes: list[RouteInfo] = []
    decorator = re.compile(
        r'@router\.(get|post|put|patch|delete)\(\s*["\']([^"\']+)["\']',
        re.I,
    )
    func = re.compile(r"^async def (\w+)", re.M)

    for py in sorted(ROUTE_DIR.glob("*.py")):
        if py.name == "__init__.py":
            continue
        text = py.read_text(encoding="utf-8")
        for m in decorator.finditer(text):
            method = m.group(1).upper()
            path = m.group(2)
            start = m.end()
            chunk = text[start : start + 400]
            hm = func.search(chunk)
            handler = hm.group(1) if hm else "?"
            tier, reason = _tier_for(path, handler, method)
            routes.append(
                RouteInfo(
                    method=method,
                    path=path,
                    handler=handler,
                    file=py.name,
                    tier=tier,
                    reason=reason,
                )
            )
    return routes


async def _live_bench(company_id: str) -> None:
    from app.core.config import get_settings
    from app.core.database import get_prisma_client
    from app.repositories.audit_log_repository import AuditLogRepository
    from app.repositories.coa_repository import CoaRepository
    from app.repositories.customer_repository import CustomerRepository
    from app.repositories.dashboard_overview_repository import DashboardOverviewRepository
    from app.repositories.dashboard_repository import DashboardRepository
    from app.repositories.product_repository import ProductRepository
    from app.services.activity_service import ActivityService
    from app.services.aging_service import AgingService
    from app.services.extended_reports_service import ExtendedReportsService
    from app.services.my_tasks_service import MyTasksService
    from app.services.report_query_service import ReportQueryService

    os.environ["DATABASE_URL"] = get_settings().database_url
    prisma = get_prisma_client()
    await prisma.connect()

    cases: list[tuple[str, str, object]] = [
        ("A", "dashboard.overview", DashboardOverviewRepository(prisma).overview(company_id=company_id)),
        ("A", "report.FIN_CMP", ReportQueryService(prisma=prisma).execute(
            company_id=company_id, report_id="FIN_CMP", criteria={"periodCount": 12})),
        ("A", "extended.customer_balances", ExtendedReportsService(prisma).customer_balances(
            company_id=company_id, date_from=None, date_to=None)),
        ("B", "activity.sales", ActivityService(prisma).list_sales_activity(
            company_id=company_id, include_planning=True)),
        ("B", "my_tasks", MyTasksService(prisma).list_tasks(company_id=company_id)),
        ("B", "customers.list", CustomerRepository(prisma).list_customers(company_id=company_id)),
        ("B", "products.list", ProductRepository(prisma).list_products(company_id=company_id)),
        ("B", "audit.search", AuditLogRepository(prisma).list_filtered(
            company_id=company_id, user_id=None, date_from=None, date_to=None,
            transaction_type_contains="POST", take=100)),
        ("A", "aging.ar", AgingService(prisma).ar_aging(company_id=company_id, as_of_date=None)),
        ("A", "coa.tree", CoaRepository(prisma).list_tree(company_id=company_id)),
        ("A", "dashboard.summary", DashboardRepository(prisma).summary(company_id=company_id)),
    ]

    print(f"\nLive service-layer bench (company_id={company_id})\n")
    limits = {"A": 1000.0, "B": 200.0}
    slow: list[str] = []
    for tier, label, coro in cases:
        t0 = time.perf_counter()
        await coro
        ms = (time.perf_counter() - t0) * 1000
        limit = limits[tier]
        flag = " SLOW" if ms > limit else ""
        if ms > limit:
            slow.append(label)
        print(f"  [{tier}] {label:28} {ms:8.1f} ms (limit {limit:.0f}){flag}")

    await prisma.disconnect()
    if slow:
        print(f"\n  Over SLA: {', '.join(slow)}")
    else:
        print("\n  All sampled paths within SLA.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--company-id", help="Run live service-layer samples")
    args = parser.parse_args()

    routes = _parse_routes()
    by_tier: dict[str, list[RouteInfo]] = {"A": [], "B": [], "C": []}
    for r in routes:
        by_tier[r.tier].append(r)

    print(f"Endpoint SLA audit — {len(routes)} routes\n")
    print(f"  Tier A (interactive read, <1000 ms): {len(by_tier['A'])}")
    print(f"  Tier B (search/list, <200 ms):       {len(by_tier['B'])}")
    print(f"  Tier C (excluded from 1s SLA):       {len(by_tier['C'])}")
    print("\nTier C examples (writes, exports, batch, streaming):")
    for r in by_tier["C"][:15]:
        print(f"  {r.method:6} {r.path:50} ({r.handler})")
    if len(by_tier["C"]) > 15:
        print(f"  ... and {len(by_tier['C']) - 15} more")

    print("\nNotes:")
    print("  - Steps 1–4 optimized Tier A report/dashboard paths (CTEs, indexes, replica, cache).")
    print("  - Activity feeds now cap at 500 rows/source table (ACTIVITY_FETCH_LIMIT).")
    print("  - Tier C endpoints are not expected to complete in <1s by design.")
    print("  - Run bench_hot_paths.py for full hot-path timings after migrate deploy.")

    if args.company_id:
        asyncio.run(_live_bench(args.company_id))


if __name__ == "__main__":
    main()
