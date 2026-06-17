"""P31 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.constants.rbac_audit_types import RBAC_AUDIT_TYPES


def test_rbac_audit_types_include_invite_and_import() -> None:
    assert "USER_INVITE" in RBAC_AUDIT_TYPES
    assert "ROLE_IMPORT" in RBAC_AUDIT_TYPES


@pytest.mark.asyncio
async def test_openapi_p31_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/roles/import/preview" in paths
    assert "/api/v1/companies/{company_id}/settings/welcome-email-template" in paths
    assert "/api/v1/companies/{company_id}/audit-log/rbac-types" in paths
    audit_get = paths["/api/v1/companies/{company_id}/audit-log"]["get"]
    param_names = [p.get("name") for p in audit_get.get("parameters", [])]
    assert "rbacOnly" in param_names
