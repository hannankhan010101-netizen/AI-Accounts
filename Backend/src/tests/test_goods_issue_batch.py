"""Goods issue uses invoice line batch for stock deduction — §7.8."""

from __future__ import annotations

import os
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.services.inventory_quantity_service import InventoryQuantityService


@pytest.mark.asyncio
async def test_apply_goods_issue_uses_line_batch_number() -> None:
    batches = MagicMock()
    batches.apply_product_delta = AsyncMock(
        return_value=MagicMock(batchNumber="LOT-A")
    )
    svc = InventoryQuantityService(batches=batches)
    line = MagicMock(productCode="SKU1", quantity=Decimal("3"), batchNumber="LOT-A")

    out = await svc.apply_goods_issue_invoice_lines(
        company_id="co",
        invoice_lines=[line],
        stock_product_codes={"SKU1"},
    )

    assert len(out) == 1
    assert out[0]["batchNumber"] == "LOT-A"
    call = batches.apply_product_delta.await_args
    assert call.kwargs["batch_number"] == "LOT-A"
    assert call.kwargs["delta"] == Decimal("-3")


@pytest.mark.asyncio
async def test_restore_goods_issue_uses_stored_batch() -> None:
    batches = MagicMock()
    batches.apply_product_delta = AsyncMock(
        return_value=MagicMock(batchNumber="LOT-B")
    )
    svc = InventoryQuantityService(batches=batches)
    gi_line = MagicMock(productCode="SKU2", quantity=Decimal("2"), batchNumber="LOT-B")

    await svc.restore_goods_issue_lines(company_id="co", lines=[gi_line])

    call = batches.apply_product_delta.await_args
    assert call.kwargs["batch_number"] == "LOT-B"
    assert call.kwargs["delta"] == Decimal("2")
