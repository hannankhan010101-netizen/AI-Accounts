"""P16 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.constants.report_aliases import resolve_report_handler_id
from app.constants.report_financial_registry import financial_report_coverage
from app.core.stripe_webhook import (
    parse_stripe_checkout_completed,
    parse_stripe_webhook_event,
)
from app.services.report_pivot_service import (
    build_pnl_category_pivot,
    pivot_pnl_category_to_csv,
)


def test_financial_module_numeric_aliases() -> None:
    assert resolve_report_handler_id("207") == "FIN_PNL_CAT"
    assert resolve_report_handler_id("208") == "FIN_TB12"
    assert resolve_report_handler_id("209") == "FIN_CMP"
    summary = financial_report_coverage()
    assert summary["unmappedFinancialReportIds"] == []


def test_parse_checkout_completed() -> None:
    body = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "customer": "cus_abc",
                "subscription": "sub_123",
                "metadata": {"company_id": "co_1", "plan_code": "pro"},
            }
        },
    }
    parsed = parse_stripe_checkout_completed(body)
    assert parsed["kind"] == "checkout"
    assert parsed["externalCustomerId"] == "cus_abc"
    assert parsed["planCode"] == "pro"

    routed = parse_stripe_webhook_event(body)
    assert routed["kind"] == "checkout"


def test_pivot_csv_export() -> None:
    flat = [
        {
            "period": "2025-01",
            "categoryType": "Income",
            "categoryName": "Sales",
            "amount": "100",
        },
        {
            "period": "2025-02",
            "categoryType": "Income",
            "categoryName": "Sales",
            "amount": "200",
        },
    ]
    pivot = build_pnl_category_pivot(flat)
    csv_text = pivot_pnl_category_to_csv(pivot)
    assert "categoryType,categoryName,2025-01,2025-02" in csv_text
    assert "Sales" in csv_text


@pytest.mark.asyncio
async def test_openapi_p16_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/sales-credits/{credit_id}/void" in paths
    assert (
        "/api/v1/companies/{company_id}/reports/comparative-pnl-by-category/pivot/export"
        in paths
    )
