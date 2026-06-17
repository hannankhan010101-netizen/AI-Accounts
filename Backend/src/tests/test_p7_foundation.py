"""P7 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.constants.report_aliases import resolve_report_handler_id
from app.integrations.kuickpay_client import KuickpayClient
from app.services.clickhouse_schema_service import ClickHouseSchemaService
from app.services.report_query_service import ReportQueryService


@pytest.mark.asyncio
async def test_openapi_p7_routes_registered() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/payments/kuickpay/initiate" in paths
    assert "/api/v1/companies/{company_id}/sales-invoices/{invoice_id}/fbr/poll" in paths
    assert "/api/v1/companies/{company_id}/platform/clickhouse/ensure-schema" in paths


def test_report_handlers_not_aliased_for_price_stock() -> None:
    assert resolve_report_handler_id("079") == "079"
    assert resolve_report_handler_id("082") == "082"
    assert resolve_report_handler_id("083") == "083"


def test_kuickpay_client_disabled_by_default() -> None:
    assert KuickpayClient().enabled is False


def test_clickhouse_schema_disabled_without_url() -> None:
    svc = ClickHouseSchemaService()
    assert svc.enabled is False


def test_low_stock_filter() -> None:
    svc = ReportQueryService(prisma=None)  # type: ignore[arg-type]

    async def _run() -> None:
        async def fake_stock(*, company_id: str, criteria: dict):
            _ = company_id, criteria
            return [
                {"productCode": "A", "quantityOnHand": "0"},
                {"productCode": "B", "quantityOnHand": "5"},
                {"productCode": "C", "quantityOnHand": "20"},
            ]

        svc._stock_quantity = fake_stock  # type: ignore[method-assign]
        rows = await svc._low_stock(company_id="c1", criteria={"lowStockThreshold": 10})
        codes = {r["productCode"] for r in rows}
        assert codes == {"B"}

    import asyncio

    asyncio.get_event_loop().run_until_complete(_run())
