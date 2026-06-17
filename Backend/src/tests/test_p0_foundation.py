"""P0 accounting foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.core.exceptions import ForbiddenError
from app.domain import document_workflow as wf
from app.services.permission_service import PermissionService


class _FakeMembershipRepo:
    def __init__(self, permissions: list[str] | None) -> None:
        self._permissions = permissions

    async def get_membership(self, *, company_id: str, user_id: str) -> dict | None:
        _ = company_id, user_id
        if self._permissions is None:
            return None
        return {"permissions": self._permissions}


def test_document_workflow_allows_draft_to_posted() -> None:
    wf.assert_can_transition(current=wf.DRAFT, target=wf.POSTED)


def test_document_workflow_blocks_posted_to_draft() -> None:
    with pytest.raises(ValueError, match="Cannot transition"):
        wf.assert_can_transition(current=wf.POSTED, target=wf.DRAFT)


@pytest.mark.asyncio
async def test_permission_denies_empty_role() -> None:
    svc = PermissionService(membership_repository=_FakeMembershipRepo([]))  # type: ignore[arg-type]
    with pytest.raises(ForbiddenError, match="No role assigned"):
        await svc.assert_allowed(
            company_id="c1", user_id="u1", permission="sales.invoices.create"
        )


@pytest.mark.asyncio
async def test_permission_wildcard_module() -> None:
    svc = PermissionService(membership_repository=_FakeMembershipRepo(["sales.*"]))  # type: ignore[arg-type]
    await svc.assert_allowed(
        company_id="c1", user_id="u1", permission="sales.invoices.approve"
    )


@pytest.mark.asyncio
async def test_openapi_includes_approve_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/sales-invoices/{invoice_id}/approve" in paths
    assert "/api/v1/companies/{company_id}/supplier-bills/{bill_id}/approve" in paths
