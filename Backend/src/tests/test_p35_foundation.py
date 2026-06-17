"""P35 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.constants.rbac_audit_types import RBAC_AUDIT_TYPES


def test_p35_audit_types() -> None:
    assert "USER_BULK_REVOKE" in RBAC_AUDIT_TYPES
    assert "USER_BULK_ASSIGN_ROLE" in RBAC_AUDIT_TYPES
    assert "ROLE_IMPORT_JOB" in RBAC_AUDIT_TYPES


@pytest.mark.asyncio
async def test_openapi_p35_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/users/bulk-assign-role" in paths
    assert "/api/v1/companies/{company_id}/users/bulk-revoke" in paths
