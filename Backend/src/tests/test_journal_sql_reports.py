"""Journal SQL aggregate paths — Phase 1 performance."""

from __future__ import annotations

import os
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

os.environ.setdefault("SKIP_PRISMA", "1")

from app.repositories.journal_repository import JournalRepository, _as_decimal
from app.repositories.sql import journal_queries as jq


def test_as_decimal_handles_none_and_strings() -> None:
    assert _as_decimal(None) == Decimal(0)
    assert _as_decimal("10.5") == Decimal("10.5")
    assert _as_decimal(Decimal("3")) == Decimal("3")


def test_trial_balance_sql_is_parameterized() -> None:
    assert "$1" in jq.TRIAL_BALANCE_SQL
    assert "GROUP BY jl.nominal_code" in jq.TRIAL_BALANCE_SQL
    assert "100_000" not in jq.TRIAL_BALANCE_SQL


def test_gl_full_sql_defined() -> None:
    assert "WITH opening AS" in jq.GL_FULL_SQL
    assert jq.GL_ACTIVITY_MAX_LINES == 50_000


def test_monthly_tb_sql_uses_generate_series() -> None:
    assert "generate_series" in jq.MONTHLY_TB_TOTALS_SQL.lower()


@pytest.mark.asyncio
async def test_trial_balance_maps_query_raw_rows() -> None:
    prisma = MagicMock()
    prisma.query_raw = AsyncMock(
        return_value=[
            {
                "nominalCode": "1000",
                "name": "Cash",
                "debit": Decimal("100"),
                "credit": Decimal("40"),
                "balance": Decimal("60"),
            }
        ]
    )
    repo = JournalRepository(prisma)
    rows = await repo.trial_balance(company_id="co1", as_of_date=None)
    assert rows == [
        {
            "nominalCode": "1000",
            "name": "Cash",
            "debit": "100",
            "credit": "40",
            "balance": "60",
        }
    ]
    prisma.query_raw.assert_awaited_once()


@pytest.mark.asyncio
async def test_monthly_tb_totals_maps_rows() -> None:
    prisma = MagicMock()
    prisma.query_raw = AsyncMock(
        return_value=[
            {
                "period": "2026-01",
                "periodTo": "2026-01-31",
                "accountCount": 5,
                "totalDebit": Decimal("1000"),
                "totalCredit": Decimal("1000"),
            }
        ]
    )
    repo = JournalRepository(prisma)
    from datetime import datetime, timezone

    rows = await repo.monthly_tb_totals(
        company_id="co1",
        anchor=datetime(2026, 1, 15, tzinfo=timezone.utc),
        period_count=1,
    )
    assert rows[0]["period"] == "2026-01"
    assert rows[0]["netBalance"] == "0"
