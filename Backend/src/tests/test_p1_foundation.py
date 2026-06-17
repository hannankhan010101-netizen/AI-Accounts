"""P1 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.domain import document_workflow as wf
from app.services.permission_service import PermissionService


class _FakeMembershipRepo:
    def __init__(self, permissions: list[str] | None) -> None:
        self._permissions = permissions

    async def get_membership(self, *, company_id: str, user_id: str) -> dict | None:
        _ = company_id, user_id
        return {"permissions": self._permissions or []}


@pytest.mark.asyncio
async def test_openapi_p1_routes_registered() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/bank-reconciliations" in paths
    assert "/api/v1/companies/{company_id}/reports/subledger-tieout/ar" in paths
    assert "/api/v1/companies/{company_id}/journals/{journal_id}/reverse" in paths
    assert "/api/v1/companies/{company_id}/platform/process-outbox" in paths


def test_cogs_source_type_defined() -> None:
    assert wf.SOURCE_SALES_INVOICE_COGS == "SALES_INVOICE_COGS"


@pytest.mark.asyncio
async def test_settings_journals_reverse_wildcard() -> None:
    svc = PermissionService(membership_repository=_FakeMembershipRepo(["settings.*"]))  # type: ignore[arg-type]
    await svc.assert_allowed(
        company_id="c1", user_id="u1", permission="settings.journals.reverse"
    )
