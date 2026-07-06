"""P1 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.domain import document_workflow as wf
from app.services.effective_permission_service import EffectivePermissionService
from app.services.permission_service import PermissionService


class _FakeEffective:
    matches = staticmethod(EffectivePermissionService.matches)
    filter_by_module = staticmethod(EffectivePermissionService.filter_by_module)

    def __init__(self, permissions: list[str]) -> None:
        self._permissions = permissions

    async def permissions_for_user(self, *, company_id: str, user_id: str) -> list[str]:
        _ = company_id, user_id
        return list(self._permissions)


class _FakeAccessControl:
    async def disabled_modules(self, *, company_id: str) -> set[str]:
        _ = company_id
        return set()


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
    svc = PermissionService(
        effective_permissions=_FakeEffective(["settings.*"]),  # type: ignore[arg-type]
        access_control=_FakeAccessControl(),  # type: ignore[arg-type]
    )
    await svc.assert_allowed(
        company_id="c1", user_id="u1", permission="settings.journals.reverse"
    )
