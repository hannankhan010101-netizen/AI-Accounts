"""P33 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.constants.rbac_audit_types import RBAC_AUDIT_TYPES
from app.services.import_job_service import ROLE_IMPORT_JOB_TYPE


def test_role_import_job_type_constant() -> None:
    assert ROLE_IMPORT_JOB_TYPE == "roles"


def test_user_reactivate_in_rbac_audit_types() -> None:
    assert "USER_REACTIVATE" in RBAC_AUDIT_TYPES


@pytest.mark.asyncio
async def test_openapi_p33_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/roles/import/jobs" in paths
    assert "/api/v1/companies/{company_id}/roles/import/jobs/{job_id}" in paths
    assert "/api/v1/companies/{company_id}/users/{user_id}/reactivate" in paths
    users_get = paths["/api/v1/companies/{company_id}/users"]["get"]
    param_names = [p.get("name") for p in users_get.get("parameters", [])]
    assert "page" in param_names
    assert "pageSize" in param_names
