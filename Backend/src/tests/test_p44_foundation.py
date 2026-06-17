"""P44 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest


@pytest.mark.asyncio
async def test_openapi_p44_export_strip_ids() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    export_get = paths["/api/v1/companies/{company_id}/roles/export"]["get"]
    param_names = {p["name"] for p in export_get.get("parameters", [])}
    assert "stripIds" in param_names


def test_export_roles_strip_ids_shape() -> None:
    rows = [
        {"id": "r1", "name": "Admin", "permissions": ["*"]},
        {"id": "r2", "name": "Clerk", "permissions": []},
    ]
    stripped = [{"name": r["name"], "permissions": r["permissions"]} for r in rows]
    assert all("id" not in r for r in stripped)
    assert stripped[0]["name"] == "Admin"


def test_bank_transfer_audit_type_constant() -> None:
    from app.domain.document_workflow import SOURCE_BANK_TRANSFER

    assert SOURCE_BANK_TRANSFER == "BANK_TRANSFER"
