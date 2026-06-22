"""Assistant createProduct tool handler tests."""

from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.services.assistant.tool_handlers import AssistantToolHandlers


@pytest.mark.asyncio
async def test_create_product_persists_and_returns_invalidate():
    permission_service = SimpleNamespace(
        permissions_for=AsyncMock(return_value=["inventory.products.create", "*"]),
        assert_allowed=AsyncMock(return_value=None),
    )

    auto_code = AsyncMock()
    auto_code.resolve_code.return_value = "003"

    product_repo = AsyncMock()
    product_repo.get_by_codes.return_value = []
    product_repo.create_product.return_value = SimpleNamespace(
        id="prod-1",
        code="003",
        name="Shampoo",
        cost=Decimal("0"),
        salePrice=Decimal("425"),
        unit="EA",
    )

    handlers = AssistantToolHandlers(
        permission_service=permission_service,
        sales_invoice_repository=AsyncMock(),
        product_repository=product_repo,
        audit_log_repository=AsyncMock(),
        auto_code_service=auto_code,
    )

    result = await handlers.execute(
        name="createProduct",
        arguments={"name": "Shampoo", "code": "003", "price": 425},
        company_id="co-1",
        user_id="user-1",
        pathname="/inventory/products",
    )

    assert result["ok"] is True
    assert result["product"]["code"] == "003"
    assert result["invalidate"] == ["products"]
    product_repo.create_product.assert_awaited_once()
    kwargs = product_repo.create_product.await_args.kwargs
    assert kwargs["name"] == "Shampoo"
    assert kwargs["code"] == "003"
    assert kwargs["sale_price"] == Decimal("425")


@pytest.mark.asyncio
async def test_create_product_rejects_duplicate_code():
    permission_service = SimpleNamespace(
        permissions_for=AsyncMock(return_value=["inventory.products.create"]),
        assert_allowed=AsyncMock(return_value=None),
    )

    auto_code = AsyncMock()
    auto_code.resolve_code.return_value = "003"

    product_repo = AsyncMock()
    product_repo.get_by_codes.return_value = [
        SimpleNamespace(id="existing", code="003", name="Other"),
    ]

    handlers = AssistantToolHandlers(
        permission_service=permission_service,
        sales_invoice_repository=AsyncMock(),
        product_repository=product_repo,
        audit_log_repository=AsyncMock(),
        auto_code_service=auto_code,
    )

    result = await handlers.execute(
        name="createProduct",
        arguments={"name": "Shampoo", "code": "003"},
        company_id="co-1",
        user_id="user-1",
        pathname="/inventory/products",
    )

    assert result["ok"] is False
    assert "already exists" in result["error"]
    product_repo.create_product.assert_not_awaited()
