"""P17 foundation unit tests."""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.constants.report_financial_registry import financial_report_coverage
from app.core.stripe_webhook import parse_stripe_checkout_completed


def test_financial_id_source_documented() -> None:
    summary = financial_report_coverage()
    assert "json-config" in summary["financialIdSource"]
    assert summary["unmappedFinancialReportIds"] == []


def test_checkout_completed_includes_subscription_id() -> None:
    body = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "customer": "cus_x",
                "subscription": "sub_y",
                "metadata": {"company_id": "co_1", "plan_code": "starter"},
            }
        },
    }
    parsed = parse_stripe_checkout_completed(body)
    assert parsed["subscriptionId"] == "sub_y"


@pytest.mark.asyncio
async def test_apply_checkout_fetches_period_end() -> None:
    from app.services.subscription_billing_service import SubscriptionBillingService

    prisma = MagicMock()
    prisma.subscriptionrecord.upsert = AsyncMock()
    modules = MagicMock()
    modules.list_entitlements = AsyncMock(return_value=[])
    modules.replace_entitlements = AsyncMock()

    billing = SubscriptionBillingService(prisma=prisma, module_service=modules)
    with patch.object(
        billing,
        "_fetch_stripe_subscription_period_end",
        AsyncMock(return_value=None),
    ) as fetch_mock:
        with patch.object(
            billing,
            "apply_webhook_event",
            AsyncMock(return_value={"planCode": "starter"}),
        ):
            await billing.apply_checkout_completed(
                company_id="co_1",
                plan_code="starter",
                external_customer_id="cus_x",
                subscription_id="sub_y",
            )
    fetch_mock.assert_awaited_once_with(subscription_id="sub_y")


@pytest.mark.asyncio
async def test_inventory_service_multiplier_sign() -> None:
    from decimal import Decimal

    from app.services.inventory_quantity_service import InventoryQuantityService

    batches = MagicMock()
    batches.apply_product_delta = AsyncMock(
        return_value=MagicMock(batchNumber="MAIN")
    )
    svc = InventoryQuantityService(batches=batches)
    line = MagicMock(productCode="SKU1", quantityDelta=Decimal("5"))
    await svc.apply_stock_adjustment_lines(
        company_id="co",
        lines=[line],
        multiplier=Decimal("-1"),
    )
    batches.apply_product_delta.assert_awaited_once()
    call = batches.apply_product_delta.await_args
    assert call.kwargs["delta"] == Decimal("-5")


@pytest.mark.asyncio
async def test_openapi_p17_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/sales-invoices/{invoice_id}/void" in paths
    assert "/api/v1/companies/{company_id}/supplier-bills/{bill_id}/void" in paths
