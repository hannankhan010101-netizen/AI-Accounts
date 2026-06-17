"""Phase 5 — SQL aggregates, COA flat tree, latency percentiles."""

from __future__ import annotations

import os
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

os.environ.setdefault("SKIP_PRISMA", "1")

from app.core.metrics import get_metrics, reset_metrics_for_tests
from app.repositories.sql.coa_queries import build_coa_tree_from_flat
from app.services.report_query_service import ReportQueryService


def test_build_coa_tree_from_flat_rows() -> None:
    rows = [
        {
            "categoryId": "c1",
            "categoryCode": "1",
            "categoryName": "Assets",
            "categorySortOrder": 1,
            "categoryType": "Asset",
            "sectionId": "s1",
            "sectionCode": "10",
            "sectionName": "Cash",
            "sectionSortOrder": 1,
            "nominalId": "n1",
            "nominalCode": "1000",
            "nominalName": "Bank",
            "nominalDescription": None,
            "isChargeDeduction": False,
        }
    ]
    tree = build_coa_tree_from_flat(rows)
    assert tree[0]["code"] == "1"
    assert tree[0]["sections"][0]["nominals"][0]["code"] == "1000"


def test_metrics_latency_percentiles() -> None:
    reset_metrics_for_tests()
    metrics = get_metrics()
    for ms in (10.0, 20.0, 100.0, 500.0):
        metrics.observe("http_request_duration_ms", ms, method="GET")
    pct = metrics.latency_percentiles()
    assert pct["count"] == 4
    assert pct["p50"] >= 10


@pytest.mark.asyncio
async def test_sale_summary_by_customer_sql() -> None:
    db = MagicMock()
    db.query_raw = AsyncMock(
        return_value=[{"customerId": "cust-1", "totalSales": Decimal("99")}]
    )
    rows = await ReportQueryService(prisma=db)._sale_summary_by_customer(
        company_id="co1", criteria={}
    )
    assert rows[0]["totalSales"] == "99"


@pytest.mark.asyncio
async def test_bank_cash_flow_monthly_sql() -> None:
    db = MagicMock()
    db.query_raw = AsyncMock(
        return_value=[
            {
                "month": "2026-01",
                "inflow": Decimal("100"),
                "outflow": Decimal("40"),
            }
        ]
    )
    rows = await ReportQueryService(prisma=db)._bank_cash_flow_monthly(
        company_id="co1", criteria={}
    )
    assert rows[0]["net"] == "60"


@pytest.mark.asyncio
async def test_stock_movement_sql() -> None:
    db = MagicMock()
    db.query_raw = AsyncMock(
        return_value=[
            {
                "id": "adj-1",
                "voucherNumber": "SA-1",
                "movementDate": "2026-01-10",
                "productCode": "P1",
                "quantityDelta": Decimal("-2"),
            }
        ]
    )
    rows = await ReportQueryService(prisma=db)._stock_movement(
        company_id="co1", criteria={}
    )
    assert rows[0]["kind"] == "adjustment"
    assert rows[0]["quantityDelta"] == "-2"


@pytest.mark.asyncio
async def test_stock_transfer_detail_sql() -> None:
    db = MagicMock()
    db.query_raw = AsyncMock(
        return_value=[
            {
                "id": "st-1",
                "voucherNumber": "ST-1",
                "transferDate": "2026-01-11",
                "fromLocationCode": "A",
                "toLocationCode": "B",
                "productCode": "P1",
                "quantity": Decimal("5"),
                "unitCost": Decimal("10"),
                "lineValue": Decimal("50"),
            }
        ]
    )
    rows = await ReportQueryService(prisma=db)._stock_transfer_detail(
        company_id="co1", criteria={}
    )
    assert rows[0]["lineValue"] == "50"


@pytest.mark.asyncio
async def test_product_sales_by_product_sql() -> None:
    db = MagicMock()
    db.query_raw = AsyncMock(
        return_value=[{"productCode": "P1", "totalSales": Decimal("10")}]
    )
    rows = await ReportQueryService(prisma=db)._product_sale_by_product(
        company_id="co1", criteria={}
    )
    assert rows[0]["productCode"] == "P1"
