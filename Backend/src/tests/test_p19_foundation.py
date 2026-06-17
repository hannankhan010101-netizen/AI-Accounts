"""P19 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.constants.module_permission_matrix import PLAN_MODULE_DEFAULTS
from app.services.inventory_quantity_service import InventoryQuantityService


def test_cancelled_plan_disables_all_modules() -> None:
    assert PLAN_MODULE_DEFAULTS["cancelled"] == frozenset()


def test_inventory_has_grn_apply() -> None:
    assert hasattr(InventoryQuantityService, "apply_grn_receipt_lines")


@pytest.mark.asyncio
async def test_cancelled_syncs_no_modules() -> None:
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
        event_type="customer.subscription.deleted",
    )
    call = modules.replace_entitlements.await_args
    payload = call.kwargs["entitlements"]
    enabled = {e["moduleCode"] for e in payload if e["enabled"]}
    assert enabled == set()


@pytest.mark.asyncio
async def test_openapi_p19_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert (
        "/api/v1/companies/{company_id}/sales-invoices/{invoice_id}/goods-issue/lines/{line_id}/void"
        in paths
    )
