"""P37 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.constants.rbac_audit_types import RBAC_AUDIT_TYPES


def test_role_import_job_in_rbac_audit_types() -> None:
    assert "ROLE_IMPORT_JOB" in RBAC_AUDIT_TYPES


@pytest.mark.asyncio
async def test_openapi_p37_audit_transaction_id() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    audit_get = paths["/api/v1/companies/{company_id}/audit-log"]["get"]
    param_names = {p["name"] for p in audit_get.get("parameters", [])}
    assert "transactionId" in param_names
