"""P27 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.services.permission_validation_service import (
    known_codes_sorted,
    strict_validation_error,
    validate_role_permissions,
)


def test_known_codes_sorted_is_sorted_unique() -> None:
    codes = known_codes_sorted()
    assert codes == sorted(codes)
    assert "*" in codes
    assert len(codes) == len(set(codes))


def test_strict_validation_error_blocks_unknown() -> None:
    validation = validate_role_permissions(["bogus.code"])
    assert strict_validation_error(validation) is not None
    assert "bogus.code" in strict_validation_error(validation)


def test_strict_validation_error_allows_known() -> None:
    validation = validate_role_permissions(["sales.read"])
    assert strict_validation_error(validation) is None


@pytest.mark.asyncio
async def test_openapi_p27_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/permissions/known-codes" in paths
    assert "/api/v1/companies/{company_id}/users/invite" in paths
    create_role = paths["/api/v1/companies/{company_id}/roles"]["post"]
    param_names = [p.get("name") for p in create_role.get("parameters", [])]
    assert "strict" in param_names
