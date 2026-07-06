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


def _create_handlers(product_repo: AsyncMock) -> AssistantToolHandlers:
    permission_service = SimpleNamespace(
        permissions_for=AsyncMock(return_value=["inventory.products.create", "*"]),
        assert_allowed=AsyncMock(return_value=None),
    )
    auto_code = AsyncMock()
    auto_code.resolve_code.return_value = "003"
    return AssistantToolHandlers(
        permission_service=permission_service,
        sales_invoice_repository=AsyncMock(),
        product_repository=product_repo,
        audit_log_repository=AsyncMock(),
        auto_code_service=auto_code,
    )


async def _create(product_repo: AsyncMock, arguments: dict):
    handlers = _create_handlers(product_repo)
    return await handlers.execute(
        name="createProduct",
        arguments=arguments,
        company_id="co-1",
        user_id="user-1",
        pathname="/inventory/products",
    )


@pytest.mark.parametrize(
    "bad_cost, needle",
    [
        (-5, "negative"),
        ("abc", "valid number"),
        ("NaN", "finite"),
        ("Infinity", "finite"),
        (10**15, "too large"),
    ],
)
@pytest.mark.asyncio
async def test_create_product_rejects_bad_cost(bad_cost, needle):
    product_repo = AsyncMock()
    product_repo.get_by_codes.return_value = []

    result = await _create(product_repo, {"name": "X", "code": "003", "cost": bad_cost})

    assert result["ok"] is False
    assert needle in result["error"].lower()
    product_repo.create_product.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_product_string_false_is_not_stock():
    product_repo = AsyncMock()
    product_repo.get_by_codes.return_value = []
    product_repo.create_product.return_value = SimpleNamespace(
        id="p1", code="003", name="X", cost=Decimal("0"), salePrice=Decimal("0"), unit="EA"
    )

    result = await _create(
        product_repo, {"name": "X", "code": "003", "isStock": "false"}
    )

    assert result["ok"] is True
    assert product_repo.create_product.await_args.kwargs["is_stock"] is False


@pytest.mark.asyncio
async def test_create_product_db_error_is_graceful():
    product_repo = AsyncMock()
    product_repo.get_by_codes.return_value = []
    product_repo.create_product.side_effect = RuntimeError("unique violation")

    result = await _create(product_repo, {"name": "X", "code": "003", "price": 10})

    assert result["ok"] is False
    assert "could not create" in result["error"].lower()
