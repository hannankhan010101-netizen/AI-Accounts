"""Assistant updateProduct tool handler tests."""

from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.services.assistant.tool_handlers import AssistantToolHandlers


def _handlers(product_repo: AsyncMock) -> AssistantToolHandlers:
    permission_service = SimpleNamespace(
        permissions_for=AsyncMock(return_value=["inventory.products.create", "*"]),
        assert_allowed=AsyncMock(return_value=None),
    )
    return AssistantToolHandlers(
        permission_service=permission_service,
        sales_invoice_repository=AsyncMock(),
        product_repository=product_repo,
        audit_log_repository=AsyncMock(),
        auto_code_service=AsyncMock(),
    )


@pytest.mark.asyncio
async def test_update_product_sets_cost_by_code():
    product_repo = AsyncMock()
    product_repo.get_by_codes.return_value = [
        SimpleNamespace(id="prod-9", code="2772", name="Lifeboy"),
    ]
    product_repo.update_product.return_value = SimpleNamespace(
        id="prod-9",
        code="2772",
        name="Lifeboy",
        cost=Decimal("275"),
        salePrice=Decimal("0"),
        unit="EA",
    )

    handlers = _handlers(product_repo)

    result = await handlers.execute(
        name="updateProduct",
        arguments={"code": "2772", "cost": 275},
        company_id="co-1",
        user_id="user-1",
        pathname="/inventory/products",
    )

    assert result["ok"] is True
    assert result["product"]["cost"] == "275"
    assert result["invalidate"] == ["products"]
    product_repo.update_product.assert_awaited_once()
    kwargs = product_repo.update_product.await_args.kwargs
    assert kwargs["product_id"] == "prod-9"
    assert kwargs["data"] == {"cost": Decimal("275")}


@pytest.mark.asyncio
async def test_update_product_not_found():
    product_repo = AsyncMock()
    product_repo.get_by_codes.return_value = []

    handlers = _handlers(product_repo)

    result = await handlers.execute(
        name="updateProduct",
        arguments={"code": "9999", "cost": 275},
        company_id="co-1",
        user_id="user-1",
        pathname="/inventory/products",
    )

    assert result["ok"] is False
    assert "not found" in result["error"].lower()
    product_repo.update_product.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_product_requires_a_field():
    product_repo = AsyncMock()
    product_repo.get_by_codes.return_value = [
        SimpleNamespace(id="prod-9", code="2772", name="Lifeboy"),
    ]

    handlers = _handlers(product_repo)

    result = await handlers.execute(
        name="updateProduct",
        arguments={"code": "2772"},
        company_id="co-1",
        user_id="user-1",
        pathname="/inventory/products",
    )

    assert result["ok"] is False
    assert "no fields" in result["error"].lower()
    product_repo.update_product.assert_not_awaited()


async def _update(product_repo: AsyncMock, arguments: dict):
    handlers = _handlers(product_repo)
    return await handlers.execute(
        name="updateProduct",
        arguments=arguments,
        company_id="co-1",
        user_id="user-1",
        pathname="/inventory/products",
    )


@pytest.mark.parametrize(
    "bad_cost, needle",
    [(-1, "negative"), ("xyz", "valid number"), ("NaN", "finite"), (10**15, "too large")],
)
@pytest.mark.asyncio
async def test_update_product_rejects_bad_cost(bad_cost, needle):
    product_repo = AsyncMock()
    product_repo.get_by_codes.return_value = [
        SimpleNamespace(id="prod-9", code="2772", name="Lifeboy"),
    ]

    result = await _update(product_repo, {"code": "2772", "cost": bad_cost})

    assert result["ok"] is False
    assert needle in result["error"].lower()
    product_repo.update_product.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_product_string_false_sets_not_stock():
    product_repo = AsyncMock()
    product_repo.get_by_codes.return_value = [
        SimpleNamespace(id="prod-9", code="2772", name="Lifeboy"),
    ]
    product_repo.update_product.return_value = SimpleNamespace(
        id="prod-9", code="2772", name="Lifeboy",
        cost=Decimal("0"), salePrice=Decimal("0"), unit="EA",
    )

    result = await _update(product_repo, {"code": "2772", "isStock": "false"})

    assert result["ok"] is True
    assert product_repo.update_product.await_args.kwargs["data"] == {"isStock": False}


@pytest.mark.asyncio
async def test_update_product_empty_name_rejected():
    product_repo = AsyncMock()
    product_repo.get_by_codes.return_value = [
        SimpleNamespace(id="prod-9", code="2772", name="Lifeboy"),
    ]

    result = await _update(product_repo, {"code": "2772", "name": "   "})

    assert result["ok"] is False
    assert "empty" in result["error"].lower()
    product_repo.update_product.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_product_db_error_is_graceful():
    product_repo = AsyncMock()
    product_repo.get_by_codes.return_value = [
        SimpleNamespace(id="prod-9", code="2772", name="Lifeboy"),
    ]
    product_repo.update_product.side_effect = RuntimeError("db down")

    result = await _update(product_repo, {"code": "2772", "cost": 275})

    assert result["ok"] is False
    assert "could not update" in result["error"].lower()
