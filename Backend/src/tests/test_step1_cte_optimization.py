"""Step 1 CTE consolidation — aging, GL, GRNI, dashboard overview."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

os.environ.setdefault("SKIP_PRISMA", "1")

from app.repositories.dashboard_overview_repository import DashboardOverviewRepository
from app.repositories.journal_repository import JournalRepository
from app.repositories.sql import aging_queries as aq
from app.repositories.sql import journal_queries as jq
from app.services.aging_service import AgingService, as_of_date_is_current
from app.services.grni_service import GrniService


def test_ar_aging_merged_sql_uses_cte_and_party_lookup() -> None:
    assert "WITH open AS" in aq.AR_AGING_MERGED_SQL
    assert "FULL OUTER JOIN" in aq.AR_AGING_MERGED_SQL
    assert "party AS" in aq.AR_AGING_MERGED_SQL
    assert "FROM customers" in aq.AR_AGING_MERGED_SQL


def test_ap_aging_merged_sql_uses_cte() -> None:
    assert "WITH open AS" in aq.AP_AGING_MERGED_SQL
    assert "party AS" in aq.AP_AGING_MERGED_SQL
    assert "FROM suppliers" in aq.AP_AGING_MERGED_SQL


def test_gl_full_sql_single_round_trip() -> None:
    assert "WITH opening AS" in jq.GL_FULL_SQL
    assert "activity_count AS" in jq.GL_FULL_SQL
    assert "running_balance" in jq.GL_FULL_SQL


def test_as_of_date_is_current() -> None:
    now = datetime.now(timezone.utc)
    assert as_of_date_is_current(now) is True


@pytest.mark.asyncio
async def test_ar_aging_single_query_raw() -> None:
    prisma = MagicMock()
    prisma.query_raw = AsyncMock(
        return_value=[
            {
                "partyId": "cust1",
                "partyName": "Acme",
                "partyCode": "A001",
                "invoicesTotal": Decimal("100"),
                "receiptsTotal": Decimal("20"),
                "remaining": Decimal("80"),
                "oldestOpenDate": datetime(2026, 1, 1, tzinfo=timezone.utc),
                "openInvoiceCount": 2,
            }
        ]
    )
    svc = AgingService(prisma)
    result = await svc.ar_aging(
        company_id="co1",
        as_of_date=datetime(2026, 6, 1, tzinfo=timezone.utc),
    )
    assert result["rows"][0]["partyId"] == "cust1"
    assert result["rows"][0]["balance"] == "80"
    prisma.query_raw.assert_awaited_once()
    assert prisma.query_raw.await_args.args[0] == aq.AR_AGING_MERGED_SQL


@pytest.mark.asyncio
async def test_general_ledger_uses_gl_full_sql() -> None:
    prisma = MagicMock()
    prisma.query_raw = AsyncMock(
        return_value=[
            {
                "opening": Decimal("100"),
                "activity_count": 1,
                "line_id": "line1",
                "journalId": "j1",
                "journalNumber": "J-001",
                "journalDate": datetime(2026, 2, 1, tzinfo=timezone.utc),
                "refNo": None,
                "projectCode": None,
                "debit": Decimal("50"),
                "credit": Decimal("0"),
                "running_balance": Decimal("150"),
            }
        ]
    )
    repo = JournalRepository(prisma)
    result = await repo.general_ledger(
        company_id="co1",
        nominal_code="1000",
        date_from=datetime(2026, 1, 1, tzinfo=timezone.utc),
        date_to=datetime(2026, 12, 31, tzinfo=timezone.utc),
    )
    assert result["openingBalance"] == "100"
    assert len(result["lines"]) == 1
    assert result["lines"][0]["balance"] == "150"
    prisma.query_raw.assert_awaited_once()


@pytest.mark.asyncio
async def test_grni_service_delegates_to_sql() -> None:
    prisma = MagicMock()
    prisma.query_raw = AsyncMock(
        return_value=[
            {
                "productCode": "P1",
                "receivedQty": Decimal("10"),
                "billedQty": Decimal("4"),
                "grniQty": Decimal("6"),
                "unitCost": Decimal("5"),
                "grniValue": Decimal("30"),
            }
        ]
    )
    rows = await GrniService(prisma=prisma).report(company_id="co1")
    assert rows[0]["grniQty"] == "6"
    prisma.query_raw.assert_awaited_once()


@pytest.mark.asyncio
async def test_dashboard_overview_parallel_fetch() -> None:
    prisma = MagicMock()
    prisma.query_raw = AsyncMock(
        side_effect=[
            [{"month": "2026-01", "total_sales": Decimal("100")}],
            [{"bucket": "inStock", "cnt": 3}],
            [{"bankAccountId": "b1", "name": "Main", "nominalCode": "1000",
              "currency": "PKR", "balance": Decimal("500")}],
            [{"month": "2026-01", "inflow": Decimal("100"), "outflow": Decimal("40")}],
        ]
    )

    journals = MagicMock()
    journals.classified_balances = AsyncMock(return_value=[
        {"categoryType": "Income", "debit": "0", "credit": "200",
         "categoryName": "Sales", "name": "Sales", "nominalCode": "4000"},
        {"categoryType": "Expense", "debit": "50", "credit": "0",
         "categoryName": "Rent", "name": "Rent", "nominalCode": "5000"},
    ])

    aging = MagicMock()
    aging.ar_aging = AsyncMock(return_value={"rows": [], "buckets": [], "totals": {}})
    aging.ap_aging = AsyncMock(return_value={"rows": [], "buckets": [], "totals": {}})

    repo = DashboardOverviewRepository(prisma)
    repo._journals = journals
    repo._aging = aging

    result = await repo.overview(company_id="co1")
    assert result["profitAndLoss"]["totals"]["income"] == "200"
    assert result["inventoryStock"]["inStock"] == 3
    assert len(result["bankBalances"]) == 1
