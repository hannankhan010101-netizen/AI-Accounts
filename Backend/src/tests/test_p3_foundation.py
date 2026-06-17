"""P3 foundation unit tests."""

from __future__ import annotations

import os
from decimal import Decimal

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.core.exceptions import ValidationAppError
from app.services.approval_engine_service import ApprovalEngineService
from app.services.import_excel_service import parse_upload


class _PolicyRepo:
    async def list_for_company(self, *, company_id: str):
        _ = company_id
        return []


class _RequestRepo:
    pass


@pytest.mark.asyncio
async def test_openapi_p3_routes_registered() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/approval-requests" in paths
    assert "/api/v1/companies/{company_id}/import-jobs/upload" in paths
    assert "/api/v1/companies/{company_id}/reports/grni" in paths


def test_parse_csv_rows() -> None:
    content = b"code,name\nC1,Acme\n"
    rows = parse_upload(filename="customers.csv", content=content)
    assert len(rows) == 1
    assert rows[0]["code"] == "C1"


def test_approval_not_required_without_policy() -> None:
    async def _run() -> None:
        svc = ApprovalEngineService(
            policy_repository=_PolicyRepo(),  # type: ignore[arg-type]
            request_repository=_RequestRepo(),  # type: ignore[arg-type]
        )
        assert (
            await svc.requires_approval(
                company_id="c1",
                entity_type="sales_invoice",
                amount=Decimal("999999"),
            )
            is False
        )

    import asyncio

    asyncio.get_event_loop().run_until_complete(_run())


def test_approval_threshold_from_rules() -> None:
    class _Policies:
        async def list_for_company(self, *, company_id: str):
            _ = company_id
            from types import SimpleNamespace

            return [
                SimpleNamespace(
                    entityType="sales_invoice",
                    rules={"minAmount": 1000},
                )
            ]

    async def _run() -> None:
        svc = ApprovalEngineService(
            policy_repository=_Policies(),  # type: ignore[arg-type]
            request_repository=_RequestRepo(),  # type: ignore[arg-type]
        )
        assert await svc.requires_approval(
            company_id="c1",
            entity_type="sales_invoice",
            amount=Decimal("1000"),
        )

    import asyncio

    asyncio.get_event_loop().run_until_complete(_run())
