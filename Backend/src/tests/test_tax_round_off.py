"""Tax line totals respect Smart Settings round-off sales."""

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.smart_settings_runtime import SmartSettingsRuntime
from app.services.tax_calculation_service import TaxCalculationService


@pytest.mark.asyncio
async def test_compute_sales_lines_rounds_line_totals() -> None:
    taxes_repo = AsyncMock()
    taxes_repo.get_for_company.return_value = MagicMock(
        gstRates=[
            {
                "taxCode": "GST",
                "taxRate": 17,
                "status": "active",
                "accountId": "2200",
            }
        ],
        adtRates=[],
        fedRates=[],
    )
    smart_repo = AsyncMock()
    smart_repo.get_for_company.return_value = MagicMock(
        payload={"others": {"roundOffSales": True}}
    )
    runtime = SmartSettingsRuntime(smart_settings_repository=smart_repo, prisma=AsyncMock())
    service = TaxCalculationService(taxes_repository=taxes_repo, smart_runtime=runtime)

    result = await service.compute_sales_lines(
        company_id="co1",
        raw_lines=[{"quantity": 1, "rate": "99.51", "gstCode": "GST"}],
    )

    assert len(result.lines) == 1
    assert result.lines[0].line_total == Decimal("116")
