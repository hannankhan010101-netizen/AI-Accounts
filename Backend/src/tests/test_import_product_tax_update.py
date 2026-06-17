from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.import_handlers import _import_product_tax_update


@pytest.mark.asyncio
async def test_import_product_tax_update_merges_custom_fields() -> None:
    db = AsyncMock()
    product = MagicMock(
        id="p1",
        code="P001",
        customFields={"gstCode": "OLD"},
    )
    db.product.find_first = AsyncMock(return_value=product)
    db.product.update = AsyncMock()

    result = await _import_product_tax_update(
        db=db,
        company_id="co1",
        rows=[{"productCode": "P001", "gstCode": "GST18", "whtCode": "WHT1"}],
    )

    assert result.created == 1
    assert result.skipped == 0
    db.product.update.assert_awaited_once()
    update_data = db.product.update.call_args.kwargs["data"]["customFields"]
    assert update_data["gstCode"] == "GST18"
    assert update_data["whtCode"] == "WHT1"


@pytest.mark.asyncio
async def test_import_product_tax_update_skips_unknown_product() -> None:
    db = AsyncMock()
    db.product.find_first = AsyncMock(return_value=None)

    result = await _import_product_tax_update(
        db=db,
        company_id="co1",
        rows=[{"productCode": "MISSING", "gstCode": "GST18"}],
    )

    assert result.created == 0
    assert result.skipped == 1
    assert result.errors
