"""P32 foundation unit tests."""

from __future__ import annotations

import json
import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.constants.rbac_audit_types import RBAC_AUDIT_TYPES
from app.services.role_import_parser import parse_role_import_file


def test_parse_json_roles_wrapper() -> None:
    payload = json.dumps(
        {"roles": [{"name": "Clerk", "permissions": ["sales.read"]}]}
    ).encode()
    rows = parse_role_import_file(filename="roles.json", content=payload)
    assert rows[0]["name"] == "Clerk"
    assert "sales.read" in rows[0]["permissions"]


def test_parse_csv_permissions_column() -> None:
    csv_text = "name,permissions\nSales, sales.read|sales.invoices.create\n"
    rows = parse_role_import_file(filename="roles.csv", content=csv_text.encode())
    assert rows[0]["name"] == "Sales"
    assert len(rows[0]["permissions"]) == 2


def test_rbac_audit_types_include_revoke() -> None:
    assert "USER_MEMBERSHIP_REVOKE" in RBAC_AUDIT_TYPES
    assert "USER_DEACTIVATE" in RBAC_AUDIT_TYPES


@pytest.mark.asyncio
async def test_openapi_p32_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/roles/import/upload" in paths
    assert "/api/v1/companies/{company_id}/audit-log/export" in paths
    assert "/api/v1/companies/{company_id}/users/{user_id}/membership" in paths
    assert "delete" in paths["/api/v1/companies/{company_id}/users/{user_id}/membership"]
