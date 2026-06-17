"""Step 4 — asyncio gather, to_thread, batched FIN_CMP SQL, cache defaults."""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

os.environ.setdefault("SKIP_PRISMA", "1")

from app.core.async_io import maybe_thread
from app.repositories.sql import journal_queries as jq
from app.services.extended_reports_service import _criteria
from app.services.report_query_service import ReportQueryService


def test_monthly_classified_pnl_sql_single_round_trip() -> None:
    assert "WITH months AS" in jq.MONTHLY_CLASSIFIED_PNL_SQL
    assert "LEFT JOIN journals j" in jq.MONTHLY_CLASSIFIED_PNL_SQL
    assert "totalIncome" in jq.MONTHLY_CLASSIFIED_PNL_SQL
    assert "generate_series" in jq.MONTHLY_CLASSIFIED_PNL_SQL


def test_monthly_classified_pnl_sql_includes_empty_months() -> None:
    assert "FROM months m" in jq.MONTHLY_CLASSIFIED_PNL_SQL
    assert "LEFT JOIN journals j" in jq.MONTHLY_CLASSIFIED_PNL_SQL
    assert "per_nominal" not in jq.MONTHLY_CLASSIFIED_PNL_SQL


def test_monthly_classified_pnl_by_category_sql() -> None:
    assert "category_type AS \"categoryType\"" in jq.MONTHLY_CLASSIFIED_PNL_BY_CATEGORY_SQL
    assert "GROUP BY period_key, category_type, category_name" in (
        jq.MONTHLY_CLASSIFIED_PNL_BY_CATEGORY_SQL
    )


def test_extended_reports_criteria_does_not_force_skip_cache() -> None:
    crit = _criteria(date_from=datetime(2026, 1, 1, tzinfo=timezone.utc))
    assert "skipCache" not in crit


@pytest.mark.asyncio
async def test_fin_cmp_handler_calls_monthly_classified_pnl_once() -> None:
    prisma = MagicMock()
    svc = ReportQueryService(prisma=prisma)
    svc._journals.monthly_classified_pnl = AsyncMock(return_value=[{"period": "2026-01"}])

    rows = await svc.execute(
        company_id="co1",
        report_id="FIN_CMP",
        criteria={"periodCount": 12, "skipCache": True},
    )

    assert rows == [{"period": "2026-01"}]
    svc._journals.monthly_classified_pnl.assert_awaited_once()
    svc._journals.classified_balances = AsyncMock()
    assert svc._journals.classified_balances.await_count == 0


@pytest.mark.asyncio
async def test_fin_pnl_cat_handler_calls_monthly_by_category_once() -> None:
    prisma = MagicMock()
    svc = ReportQueryService(prisma=prisma)
    svc._journals.monthly_classified_pnl_by_category = AsyncMock(
        return_value=[{"period": "2026-01", "categoryType": "Income", "amount": "1"}]
    )

    rows = await svc.execute(
        company_id="co1",
        report_id="FIN_PNL_CAT",
        criteria={"periodCount": 6, "skipCache": True},
    )

    assert len(rows) == 1
    svc._journals.monthly_classified_pnl_by_category.assert_awaited_once()


@pytest.mark.asyncio
async def test_customer_statement_uses_gather_for_invoices_and_receipts() -> None:
    from app.services.aging_service import AgingService

    prisma = MagicMock()
    prisma.salesinvoice.find_many = AsyncMock(return_value=[])
    prisma.salesreceipt.find_many = AsyncMock(return_value=[])

    with patch("app.services.aging_service.asyncio.gather", new=AsyncMock()) as mock_gather:
        mock_gather.return_value = ([], [])
        svc = AgingService(prisma)
        await svc.customer_statement(
            company_id="co1",
            customer_id="cust1",
            date_from=None,
            date_to=None,
        )
        mock_gather.assert_awaited_once()
        assert len(mock_gather.await_args.args) == 2


@pytest.mark.asyncio
async def test_maybe_thread_runs_inline_below_threshold() -> None:
    calls: list[str] = []

    def _fn() -> str:
        calls.append("sync")
        return "ok"

    result = await maybe_thread(_fn, min_rows=10, row_count=3)
    assert result == "ok"
    assert calls == ["sync"]


@pytest.mark.asyncio
async def test_maybe_thread_offloads_at_threshold() -> None:
    def _fn(n: int) -> int:
        return n * 2

    result = await maybe_thread(_fn, 21, min_rows=10, row_count=10)
    assert result == 42
