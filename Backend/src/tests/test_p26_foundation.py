"""P26 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.services.permission_validation_service import (
    known_permission_codes,
    validate_role_permissions,
)


def test_known_codes_include_wildcard() -> None:
    codes = known_permission_codes()
    assert "*" in codes
    assert "sales.read" in codes


def test_validate_unknown_permission() -> None:
    out = validate_role_permissions(["sales.read", "not.a.real.code"])
    assert "not.a.real.code" in out["unknownPermissions"]
    assert len(out["permissionWarnings"]) == 1


@pytest.mark.asyncio
async def test_openapi_assign_role_route() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/users/{user_id}/role" in paths
    assert "patch" in paths["/api/v1/companies/{company_id}/users/{user_id}/role"]
