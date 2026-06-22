"""Unit tests for ProductService."""

from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import ValidationAppError
from app.services.product_service import ProductService


def _product(**kwargs):
    defaults = {
        "id": "p1",
        "companyId": "co1",
        "code": "SKU-1",
        "name": "Widget",
        "unit": "EA",
        "salePrice": Decimal("10"),
        "cost": Decimal("5"),
        "isStock": True,
        "isArchived": False,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


@pytest.mark.asyncio
async def test_create_product_with_opening_stock() -> None:
    products = MagicMock()
    products.code_exists = AsyncMock(return_value=False)
    products.create_product = AsyncMock(return_value=_product())
    batches = MagicMock()
    batches.list_batches = AsyncMock(return_value=[])
    batches.create_batch = AsyncMock()
    uoms = MagicMock()
    uoms.upsert_uom = AsyncMock()
    auto_code = MagicMock()
    auto_code.resolve_code = AsyncMock(return_value="SKU-1")
    audit = MagicMock()
    audit.record = AsyncMock()
    masking = MagicMock()
    masking.field_access_for_user = AsyncMock(return_value=None)

    svc = ProductService(
        product_repository=products,
        batch_repository=batches,
        attachment_repository=MagicMock(),
        uom_service=uoms,
        auto_code_service=auto_code,
        audit_service=audit,
        field_masking=masking,
    )

    row = await svc.create_product(
        company_id="co1",
        user_id="u1",
        code=None,
        name="Widget",
        is_stock=True,
        sale_price=10,
        cost=5,
        opening_stock={"quantity": 100, "rate": 5},
    )
    assert row.code == "SKU-1"
    batches.create_batch.assert_called_once()
    audit.record.assert_called_once()


@pytest.mark.asyncio
async def test_create_product_duplicate_code_raises() -> None:
    products = MagicMock()
    products.code_exists = AsyncMock(return_value=True)
    auto_code = MagicMock()
    auto_code.resolve_code = AsyncMock(return_value="SKU-1")

    svc = ProductService(
        product_repository=products,
        batch_repository=MagicMock(),
        attachment_repository=MagicMock(),
        uom_service=MagicMock(),
        auto_code_service=auto_code,
        audit_service=MagicMock(),
        field_masking=MagicMock(),
    )

    with pytest.raises(ValidationAppError, match="already exists"):
        await svc.create_product(
            company_id="co1",
            user_id="u1",
            code="SKU-1",
            name="Widget",
            is_stock=True,
        )


@pytest.mark.asyncio
async def test_archive_product() -> None:
    products = MagicMock()
    products.get_by_id = AsyncMock(return_value=_product())
    products.set_archived = AsyncMock(return_value=_product(isArchived=True))
    audit = MagicMock()
    audit.record = AsyncMock()

    svc = ProductService(
        product_repository=products,
        batch_repository=MagicMock(),
        attachment_repository=MagicMock(),
        uom_service=MagicMock(),
        auto_code_service=MagicMock(),
        audit_service=audit,
        field_masking=MagicMock(),
    )
    row = await svc.archive_product(company_id="co1", user_id="u1", product_id="p1")
    assert row.isArchived is True
