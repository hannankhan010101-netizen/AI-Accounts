"""Phase 3 — MV, remaining amount, maintenance, bulk import."""

from __future__ import annotations

import os
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

os.environ.setdefault("SKIP_PRISMA", "1")

from app.services.import_handlers import _import_master_codes, ImportHandlerResult
from app.services.maintenance_service import MaintenanceService
from app.services.materialized_view_service import MaterializedViewService
from app.services.subledger_remaining_service import SubledgerRemainingService


@pytest.mark.asyncio
async def test_subledger_remaining_sync_invoice() -> None:
    db = MagicMock()
    inv = MagicMock()
    inv.totalAmount = Decimal("100")
    inv.allocations = [MagicMock(amount=Decimal("30"))]
    db.salesinvoice.find_unique = AsyncMock(return_value=inv)
    db.salesinvoice.update = AsyncMock()
    svc = SubledgerRemainingService(db)
    await svc.sync_sales_invoice(invoice_id="inv-1")
    db.salesinvoice.update.assert_awaited_once()
    assert db.salesinvoice.update.await_args.kwargs["data"]["remainingAmount"] == Decimal(
        "70"
    )


@pytest.mark.asyncio
async def test_mv_refresh_all() -> None:
    db = MagicMock()
    db.execute_raw = AsyncMock(return_value=0)
    result = await MaterializedViewService(db).refresh_all()
    assert result["mv_nominal_balances"] is True
    assert db.execute_raw.await_count == 3


@pytest.mark.asyncio
async def test_trial_balance_from_mv_maps_rows() -> None:
    db = MagicMock()
    db.query_raw = AsyncMock(
        return_value=[
            {
                "nominalCode": "1000",
                "name": "Cash",
                "debit": Decimal(10),
                "credit": Decimal(2),
                "balance": Decimal(8),
            }
        ]
    )
    rows = await MaterializedViewService(db).trial_balance_from_mv(company_id="co1")
    assert rows is not None
    assert rows[0]["balance"] == "8"


@pytest.mark.asyncio
async def test_maintenance_retention() -> None:
    db = MagicMock()
    db.execute_raw = AsyncMock(side_effect=[5, 10])
    stats = await MaintenanceService(db).run_retention()
    assert stats["outboxDeleted"] == 5
    assert stats["auditDeleted"] == 10


@pytest.mark.asyncio
async def test_import_master_codes_bulk() -> None:
    model = MagicMock()
    model.find_many = AsyncMock(return_value=[])
    model.create_many = AsyncMock()
    rows = [{"code": "C1", "name": "One"}, {"code": "C2", "name": "Two"}]
    result = await _import_master_codes(
        db=MagicMock(),
        company_id="co1",
        rows=rows,
        model=model,
        code_keys=("code",),
        name_keys=("name",),
    )
    assert result.created == 2
    model.create_many.assert_awaited_once()
