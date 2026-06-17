"""P23 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.models.requests.delivery_requests import GoodsReceiptNoteCreateRequest
from app.services.inventory_stock_guard_service import InventoryStockGuardService


def test_grn_request_skip_stock_flag() -> None:
    assert "skip_stock_movement" in GoodsReceiptNoteCreateRequest.model_fields


def test_stock_guard_has_grn_assert() -> None:
    assert hasattr(InventoryStockGuardService, "assert_grn_receipt_allowed")


@pytest.mark.asyncio
async def test_platform_policy_doc_exists() -> None:
    from pathlib import Path

    policy = (
        Path(__file__).resolve().parents[2] / "docs" / "PLATFORM-WEBHOOK-POLICY.md"
    )
    assert policy.is_file()
    text = policy.read_text(encoding="utf-8")
    assert "settings.platform.process" in text
    assert "/billing/webhook" in text
