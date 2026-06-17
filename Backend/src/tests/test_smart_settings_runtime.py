"""Smart Settings runtime — credit limit and flags."""

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import ValidationAppError
from app.services.smart_settings_runtime import SmartSettingsRuntime


@pytest.mark.asyncio
async def test_credit_limit_blocks_when_exceeded() -> None:
    smart_repo = AsyncMock()
    smart_repo.get_for_company.return_value = MagicMock(
        payload={"others": {"applyCreditLimit": True}}
    )
    prisma = AsyncMock()
    prisma.customer.find_first.return_value = MagicMock(
        customFields={"creditLimit": "1000"}
    )

    runtime = SmartSettingsRuntime(smart_settings_repository=smart_repo, prisma=prisma)
    runtime._aging.ar_aging = AsyncMock(
        return_value={
            "rows": [{"partyId": "cust1", "balance": "900"}],
        }
    )

    with pytest.raises(ValidationAppError, match="Credit limit exceeded"):
        await runtime.assert_credit_limit(
            company_id="co1",
            customer_id="cust1",
            additional_amount=Decimal("200"),
        )


@pytest.mark.asyncio
async def test_post_gl_on_create_false_when_template_draft() -> None:
    smart_repo = AsyncMock()
    smart_repo.get_for_company.return_value = MagicMock(
        payload={"templateDraft": {"bankPayment": True}}
    )
    runtime = SmartSettingsRuntime(smart_settings_repository=smart_repo, prisma=AsyncMock())
    assert not await runtime.post_gl_on_create(company_id="co1", module_key="bankPayment")
    assert await runtime.post_gl_on_create(company_id="co1", module_key="saleInvoices")


@pytest.mark.asyncio
async def test_post_gl_on_create_false_for_settlement_template_draft() -> None:
    smart_repo = AsyncMock()
    smart_repo.get_for_company.return_value = MagicMock(
        payload={
            "templateDraft": {
                "saleReceipts": True,
                "supplierPayments": True,
            }
        }
    )
    runtime = SmartSettingsRuntime(smart_settings_repository=smart_repo, prisma=AsyncMock())
    assert not await runtime.post_gl_on_create(company_id="co1", module_key="saleReceipts")
    assert not await runtime.post_gl_on_create(company_id="co1", module_key="supplierPayments")


@pytest.mark.asyncio
async def test_so_credit_limit_uses_apply_so_flag() -> None:
    smart_repo = AsyncMock()
    smart_repo.get_for_company.return_value = MagicMock(
        payload={"others": {"applySoCreditLimit": True}}
    )
    prisma = AsyncMock()
    prisma.customer.find_first.return_value = MagicMock(
        customFields={"creditLimit": "500"}
    )

    runtime = SmartSettingsRuntime(smart_settings_repository=smart_repo, prisma=prisma)
    runtime._aging.ar_aging = AsyncMock(
        return_value={"rows": [{"partyId": "cust1", "balance": "400"}]}
    )

    with pytest.raises(ValidationAppError, match="Credit limit exceeded"):
        await runtime.assert_credit_limit(
            company_id="co1",
            customer_id="cust1",
            additional_amount=Decimal("200"),
            for_sales_order=True,
        )


@pytest.mark.asyncio
async def test_invoice_credit_limit_ignores_so_flag_only() -> None:
    smart_repo = AsyncMock()
    smart_repo.get_for_company.return_value = MagicMock(
        payload={"others": {"applySoCreditLimit": True}}
    )
    runtime = SmartSettingsRuntime(smart_settings_repository=smart_repo, prisma=AsyncMock())
    runtime._aging.ar_aging = AsyncMock(return_value={"rows": []})

    await runtime.assert_credit_limit(
        company_id="co1",
        customer_id="cust1",
        additional_amount=Decimal("99999"),
        for_sales_order=False,
    )
    runtime._aging.ar_aging.assert_not_called()


def test_apply_round_off_whole_currency() -> None:
    runtime = SmartSettingsRuntime(
        smart_settings_repository=AsyncMock(),
        prisma=AsyncMock(),
    )
    assert runtime.apply_round_off(Decimal("99.6")) == Decimal("100")
