#!/usr/bin/env python3
"""Benchmark hot read paths (Phase 5 + Step 1 CTE + Step 2 index baselines).

Usage:
  cd Backend
  python scripts/bench_hot_paths.py --company-id <uuid>
  python scripts/bench_hot_paths.py --company-id <uuid> --explain

Requires DATABASE_URL and migrated schema.

Note: with Supabase connection_limit=1, in-request asyncio.gather for DB calls
serializes on one connection; batched SQL (FIN_CMP) still wins over loops.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from app.core.config import get_settings
from app.core.database import get_prisma_client
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.coa_repository import CoaRepository
from app.repositories.dashboard_overview_repository import DashboardOverviewRepository
from app.repositories.dashboard_repository import DashboardRepository
from app.services.activity_service import ActivityService
from app.services.aging_service import AgingService
from app.services.grni_service import GrniService
from app.services.my_tasks_service import MyTasksService
from app.services.performance_baseline_service import PerformanceBaselineService
from app.services.report_query_service import ReportQueryService

TARGET_MS = 1000.0
SEARCH_TARGET_MS = 200.0


async def _run(company_id: str, *, explain: bool) -> None:
    settings = get_settings()
    os.environ["DATABASE_URL"] = settings.database_url
    prisma = get_prisma_client()
    await prisma.connect()

    timings: list[tuple[str, float]] = []

    async def _time(label: str, coro) -> None:
        started = time.perf_counter()
        await coro
        timings.append((label, (time.perf_counter() - started) * 1000))

    await _time(
        "dashboard.summary",
        DashboardRepository(prisma).summary(company_id=company_id),
    )
    await _time(
        "dashboard.overview",
        DashboardOverviewRepository(prisma).overview(company_id=company_id),
    )
    await _time(
        "coa.list_tree",
        CoaRepository(prisma).list_tree(company_id=company_id),
    )
    await _time(
        "aging.ar",
        AgingService(prisma).ar_aging(company_id=company_id, as_of_date=None),
    )
    await _time(
        "aging.ap",
        AgingService(prisma).ap_aging(company_id=company_id, as_of_date=None),
    )
    await _time(
        "report.TB",
        ReportQueryService(prisma=prisma).execute(
            company_id=company_id, report_id="TB", criteria={"skipCache": True}
        ),
    )
    await _time(
        "report.GL",
        ReportQueryService(prisma=prisma).execute(
            company_id=company_id,
            report_id="GL",
            criteria={"skipCache": True, "nominalCode": "1000"},
        ),
    )
    await _time(
        "report.GRNI",
        GrniService(prisma=prisma).report(company_id=company_id),
    )
    await _time(
        "report.FIN_CMP",
        ReportQueryService(prisma=prisma).execute(
            company_id=company_id,
            report_id="FIN_CMP",
            criteria={"skipCache": True, "periodCount": 12},
        ),
    )
    await _time(
        "report.FIN_PNL_CAT",
        ReportQueryService(prisma=prisma).execute(
            company_id=company_id,
            report_id="FIN_PNL_CAT",
            criteria={"skipCache": True, "periodCount": 12},
        ),
    )

    # Step 2 — list / search paths
    await _time(
        "my_tasks.list",
        MyTasksService(prisma).list_tasks(company_id=company_id),
    )
    await _time(
        "audit.type_contains",
        AuditLogRepository(prisma).list_filtered(
            company_id=company_id,
            user_id=None,
            date_from=None,
            date_to=None,
            transaction_type_contains="POST",
            take=100,
        ),
    )
    await _time(
        "activity.sales",
        ActivityService(prisma).list_sales_activity(
            company_id=company_id,
            include_planning=True,
        ),
    )
    first_page = await ReportQueryService(prisma=prisma).execute(
        company_id=company_id,
        report_id="028",
        criteria={"skipCache": True, "pageSize": 50},
    )
    cursor_date = None
    cursor_id = None
    if first_page and isinstance(first_page[0], dict):
        cursor_date = first_page[0].get("invoiceDate")
        cursor_id = first_page[0].get("id")
    if cursor_date and cursor_id:
        await _time(
            "report.028.keyset",
            ReportQueryService(prisma=prisma).execute(
                company_id=company_id,
                report_id="028",
                criteria={
                    "skipCache": True,
                    "pageSize": 50,
                    "cursorDate": cursor_date,
                    "cursorId": cursor_id,
                },
            ),
        )

    if explain:
        await _explain_samples(prisma, company_id)

    bench = PerformanceBaselineService(prisma=prisma)
    report_rows = await bench.bench_report_paths(
        company_id=company_id,
        report_service_factory=None,
    )

    await prisma.disconnect()

    print(f"\nBenchmark company_id={company_id}\n")
    slow: list[str] = []
    for label, ms in timings:
        limit = SEARCH_TARGET_MS if label.startswith(("my_tasks", "audit", "report.028", "activity")) else TARGET_MS
        flag = " SLOW" if ms > limit else ""
        if ms > limit:
            slow.append(label)
        print(f"  {label:24} {ms:8.1f} ms{flag}")
    print("\n  Report handlers:")
    for row in report_rows:
        status = "ok" if row["ok"] else "FAIL"
        slow_flag = " SLOW" if row["elapsedMs"] > TARGET_MS else ""
        if row["elapsedMs"] > TARGET_MS:
            slow.append(f"report.{row['reportId']}")
        print(
            f"    {row['reportId']:6} {status:4} {row['elapsedMs']:8.1f} ms  rows={row['rowCount']}{slow_flag}"
        )
        if row.get("error"):
            print(f"           {row['error']}")
    if slow:
        print(f"\n  Paths over target: {', '.join(slow)}")
    else:
        print(f"\n  All measured paths within target.")


async def _explain_samples(prisma, company_id: str) -> None:
    queries = (
        (
            "sales_invoices keyset",
            """
            EXPLAIN (ANALYZE, BUFFERS)
            SELECT id FROM sales_invoices
            WHERE company_id = $1 AND status = 'posted'
            ORDER BY invoice_date DESC, id DESC
            LIMIT 50
            """,
            company_id,
        ),
        (
            "audit typeContains",
            """
            EXPLAIN (ANALYZE, BUFFERS)
            SELECT id FROM audit_log_entries
            WHERE company_id = $1 AND transaction_type ILIKE '%POST%'
            ORDER BY created_at DESC
            LIMIT 100
            """,
            company_id,
        ),
        (
            "AR aging party snapshot",
            """
            EXPLAIN (ANALYZE, BUFFERS)
            WITH party AS (
              SELECT customer_id AS party_id,
                     MAX(customer_code) AS party_code,
                     MAX(customer_name) AS party_name
              FROM sales_invoices
              WHERE company_id = $1 AND customer_code IS NOT NULL
              GROUP BY customer_id
            )
            SELECT party_id, party_code, party_name FROM party LIMIT 50
            """,
            company_id,
        ),
    )
    print("\n  EXPLAIN samples:")
    for label, sql, param in queries:
        try:
            rows = await prisma.query_raw(sql, param)
            plan = rows[0].get("QUERY PLAN") if rows else str(rows)
            print(f"    {label}:")
            print(f"      {plan}")
        except Exception as exc:  # noqa: BLE001
            print(f"    {label}: skipped ({exc})")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--company-id", required=True)
    parser.add_argument(
        "--explain",
        action="store_true",
        help="Run EXPLAIN ANALYZE on representative Step 2 queries",
    )
    args = parser.parse_args()
    asyncio.run(_run(args.company_id, explain=args.explain))


if __name__ == "__main__":
    main()
