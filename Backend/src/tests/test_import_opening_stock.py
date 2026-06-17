from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.import_handlers import _import_opening_stock


@pytest.mark.asyncio
async def test_import_opening_stock_creates_batch() -> None:
    db = AsyncMock()
    db.product.find_many = AsyncMock(return_value=[MagicMock(code="P001")])
    db.productbatch.find_first = AsyncMock(return_value=None)
    db.productbatch.create = AsyncMock()

    result = await _import_opening_stock(
        db=db,
        company_id="co1",
        rows=[{"productCode": "P001", "quantity": "10", "batchNumber": "B1"}],
    )

    assert result.created == 1
    assert result.skipped == 0
    db.productbatch.create.assert_awaited_once()
    create_data = db.productbatch.create.call_args.kwargs["data"]
    assert create_data["productCode"] == "P001"
    assert create_data["batchNumber"] == "B1"
    assert create_data["quantityOnHand"] == Decimal("10")


@pytest.mark.asyncio
async def test_import_opening_stock_skips_unknown_product() -> None:
    db = AsyncMock()
    db.product.find_many = AsyncMock(return_value=[])

    result = await _import_opening_stock(
        db=db,
        company_id="co1",
        rows=[{"productCode": "MISSING", "quantity": "5"}],
    )

    assert result.created == 0
    assert result.skipped == 1
    assert result.errors
