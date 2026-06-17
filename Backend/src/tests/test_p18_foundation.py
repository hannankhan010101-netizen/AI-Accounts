"""P18 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.constants.financial_report_overrides import financial_live_aliases
from app.constants.module_permission_matrix import PLAN_MODULE_DEFAULTS
from app.constants.report_aliases import resolve_report_handler_id
from app.core.stripe_webhook import (
    parse_stripe_invoice_payment_failed,
    parse_stripe_webhook_event,
)


def test_financial_live_json_aliases() -> None:
    live = financial_live_aliases()
    assert live["203"] == "TB"
    assert resolve_report_handler_id("208") == "FIN_TB12"


def test_past_due_plan_disables_modules() -> None:
    assert PLAN_MODULE_DEFAULTS["past_due"] == frozenset({"financial"})


def test_parse_invoice_payment_failed() -> None:
    body = {
        "type": "invoice.payment_failed",
        "data": {
            "object": {
                "customer": "cus_fail",
                "subscription": "sub_1",
            }
        },
    }
    parsed = parse_stripe_invoice_payment_failed(body)
    assert parsed["kind"] == "invoice_failed"
    assert parsed["externalCustomerId"] == "cus_fail"
    routed = parse_stripe_webhook_event(body)
    assert routed["kind"] == "invoice_failed"


@pytest.mark.asyncio
async def test_past_due_syncs_limited_modules() -> None:
    from unittest.mock import AsyncMock, MagicMock

    from app.services.subscription_billing_service import SubscriptionBillingService

    prisma = MagicMock()
    prisma.subscriptionrecord.upsert = AsyncMock()
    prisma.subscriptionrecord.find_unique = AsyncMock(return_value=None)
    prisma.companymembership.count = AsyncMock(return_value=1)
    modules = MagicMock()
    modules.list_entitlements = AsyncMock(return_value=[])
    modules.replace_entitlements = AsyncMock()

    billing = SubscriptionBillingService(prisma=prisma, module_service=modules)
    await billing.apply_webhook_event(
        company_id="co_1",
        event_type="invoice.payment_failed",
        external_customer_id="cus_x",
    )
    call = modules.replace_entitlements.await_args
    payload = call.kwargs["entitlements"]
    enabled = {e["moduleCode"] for e in payload if e["enabled"]}
    assert enabled == {"financial"}


@pytest.mark.asyncio
async def test_openapi_p18_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert (
        "/api/v1/companies/{company_id}/sales-invoices/{invoice_id}/void-goods-issue"
        in paths
    )
