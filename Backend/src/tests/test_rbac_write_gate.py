"""RBAC write-gate separation — read-tier permissions must not authorize writes.

Regression tests for the privilege-escalation fix: require_module_access
(ModuleAccessService.assert_access) gates MUTATING routes, so a read-only
permission (inventory.products.read, reports.*) must be rejected there, even
though those same permissions still grant module *visibility* in the nav matrix.
"""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

from unittest.mock import AsyncMock

import pytest

from app.constants.module_permission_matrix import (
    MODULE_PERMISSION_MATRIX,
    MODULE_WRITE_PERMISSIONS,
)
from app.core.exceptions import ForbiddenError
from app.services.effective_permission_service import EffectivePermissionService
from app.services.module_access_service import ModuleAccessService
from app.services.permission_service import PermissionService


def test_visibility_matrix_keeps_read_tier_but_write_gate_strips_it() -> None:
    # Visibility matrix retains read-tier perms so read-only roles still see the module.
    assert "inventory.products.read" in MODULE_PERMISSION_MATRIX["inventory"]
    assert "reports.*" in MODULE_PERMISSION_MATRIX["financial"]
    # Write gate strips them out...
    assert "inventory.products.read" not in MODULE_WRITE_PERMISSIONS["inventory"]
    assert "reports.*" not in MODULE_WRITE_PERMISSIONS["financial"]
    # ...but keeps the genuine write permissions.
    assert "inventory.products.create" in MODULE_WRITE_PERMISSIONS["inventory"]
    assert "settings.journals.create" in MODULE_WRITE_PERMISSIONS["financial"]
    # Every module still has a write entry.
    assert set(MODULE_WRITE_PERMISSIONS) == set(MODULE_PERMISSION_MATRIX)


class _FakeAccessControl:
    # Plain async no-ops (AsyncMock treats assert_* names as assertion helpers).
    async def assert_module_api_enabled(self, **_kwargs):
        return None


class _FakeModuleService:
    async def assert_enabled(self, **_kwargs):
        return None


def _access_service(perms: list[str]) -> ModuleAccessService:
    class _Eff:
        matches = staticmethod(EffectivePermissionService.matches)
        filter_by_module = staticmethod(EffectivePermissionService.filter_by_module)

    perm_svc = PermissionService(
        effective_permissions=_Eff(),  # type: ignore[arg-type]
        access_control=AsyncMock(),
    )

    async def _perms(**_kwargs):
        return list(perms)

    perm_svc.permissions_for = _perms  # type: ignore[method-assign]

    return ModuleAccessService(
        module_service=_FakeModuleService(),  # type: ignore[arg-type]
        permission_service=perm_svc,
        access_control=_FakeAccessControl(),  # type: ignore[arg-type]
    )


async def _assert(perms: list[str], module: str) -> None:
    await _access_service(perms).assert_access(
        company_id="c1", user_id="u1", module_code=module
    )


@pytest.mark.asyncio
async def test_read_only_inventory_user_denied_write() -> None:
    with pytest.raises(ForbiddenError):
        await _assert(["inventory.products.read"], "inventory")


@pytest.mark.asyncio
async def test_inventory_create_user_allowed_write() -> None:
    await _assert(["inventory.products.create"], "inventory")  # no raise


@pytest.mark.asyncio
async def test_reports_only_user_denied_financial_write() -> None:
    with pytest.raises(ForbiddenError):
        await _assert(["reports.*"], "financial")


@pytest.mark.asyncio
async def test_journal_create_user_allowed_financial_write() -> None:
    await _assert(["settings.journals.create"], "financial")  # no raise


@pytest.mark.asyncio
async def test_star_still_allowed_everywhere() -> None:
    await _assert(["*"], "inventory")
    await _assert(["*"], "financial")


@pytest.mark.asyncio
async def test_unknown_module_fails_closed() -> None:
    # Even a super admin is denied an unknown/typo module code (defence in depth).
    with pytest.raises(ForbiddenError):
        await _assert(["*"], "crm")
