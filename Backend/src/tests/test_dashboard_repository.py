"""Dashboard aggregate SQL — Phase 1."""

from __future__ import annotations

import os
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

os.environ.setdefault("SKIP_PRISMA", "1")

from app.repositories.dashboard_repository import DashboardRepository


@pytest.mark.asyncio
async def test_summary_maps_aggregate_row() -> None:
    prisma = MagicMock()
    prisma.query_raw = AsyncMock(
        return_value=[
            {
                "customers": 2,
                "suppliers": 1,
                "products": 10,
                "bankAccounts": 1,
                "journals": 5,
                "salesInvoices": 3,
                "supplierBills": 2,
                "bankPayments": 4,
                "salesAmount": Decimal("500"),
                "purchasesAmount": Decimal("200"),
                "bankPaymentsAmount": Decimal("50"),
            }
        ]
    )
    repo = DashboardRepository(prisma)
    result = await repo.summary(company_id="co1")
    assert result["counts"]["customers"] == 2
    assert result["totals"]["salesAmount"] == "500"
