"""P22 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.models.requests.delivery_requests import DeliveryNoteCreateRequest
from app.services.inventory_stock_guard_service import InventoryStockGuardService


def test_delivery_request_skip_stock_flag() -> None:
    fields = DeliveryNoteCreateRequest.model_fields
    assert "skip_stock_movement" in fields


def test_stock_guard_service_exists() -> None:
    assert hasattr(InventoryStockGuardService, "assert_delivery_stock_allowed")
    assert hasattr(InventoryStockGuardService, "assert_goods_issue_allowed")


@pytest.mark.asyncio
async def test_openapi_goods_issue_skip_stock_query() -> None:
    from app.main import app

    params = app.openapi()["paths"][
        "/api/v1/companies/{company_id}/sales-invoices/{invoice_id}/goods-issue"
    ]["post"]["parameters"]
    names = {p["name"] for p in params}
    assert "skipStockMovement" in names
