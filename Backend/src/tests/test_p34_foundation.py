"""P34 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.constants.rbac_audit_types import RBAC_AUDIT_TYPES
from app.constants.role_import import ROLE_IMPORT_ASYNC_THRESHOLD


def test_async_threshold_is_positive() -> None:
    assert ROLE_IMPORT_ASYNC_THRESHOLD >= 10


def test_user_reinvite_audit_type() -> None:
    assert "USER_REINVITE" in RBAC_AUDIT_TYPES


@pytest.mark.asyncio
async def test_openapi_p34_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/users/{user_id}/reinvite" in paths
    upload = paths["/api/v1/companies/{company_id}/roles/import/upload"]["post"]
    param_names = [p.get("name") for p in upload.get("parameters", [])]
    assert "forceSync" in param_names
    users_get = paths["/api/v1/companies/{company_id}/users"]["get"]
    user_params = [p.get("name") for p in users_get.get("parameters", [])]
    assert "q" in user_params
    assert "isActive" in user_params
