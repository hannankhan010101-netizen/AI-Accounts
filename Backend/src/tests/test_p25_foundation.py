"""P25 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.constants.permission_catalog import MODULE_LIST_READ_PERMISSIONS, PERMISSION_TREE
from app.services.module_access_service import ModuleAccessService


def test_permission_tree_has_groups() -> None:
    from app.constants.permission_catalog import flatten_permission_entries

    assert len(PERMISSION_TREE) >= 5
    codes = {row["code"] for row in flatten_permission_entries()}
    assert "settings.roles.manage" in codes
    assert "sales.read" in codes
    assert "sales.quotations.read" in codes
    assert "purchases.grn.read" in codes
    sales = next(g for g in PERMISSION_TREE if g["group"] == "Sales")
    assert len(sales.get("submodules", [])) >= 5


def test_list_read_permissions_cover_modules() -> None:
    assert "sales" in MODULE_LIST_READ_PERMISSIONS
    assert "*" in MODULE_LIST_READ_PERMISSIONS["sales"]


def test_module_access_has_list_read() -> None:
    assert hasattr(ModuleAccessService, "assert_list_read")


@pytest.mark.asyncio
async def test_openapi_p25_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/permissions/catalog" in paths
    assert "/api/v1/companies/{company_id}/roles/{role_id}" in paths
