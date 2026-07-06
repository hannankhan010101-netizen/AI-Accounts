"""Combined module entitlement + RBAC matrix + company module config — P12 / RBAC v2."""

from __future__ import annotations

from typing import Any

from app.constants.module_codes import ALL_MODULE_CODES
from app.constants.module_permission_matrix import (
    MODULE_PERMISSION_MATRIX,
    MODULE_WRITE_PERMISSIONS,
)
from app.constants.permission_catalog import MODULE_LIST_READ_PERMISSIONS
from app.core.exceptions import ForbiddenError
from app.services.access_control_service import AccessControlService
from app.services.module_entitlement_service import ModuleEntitlementService
from app.services.permission_service import PermissionService
from app.services.effective_permission_service import EffectivePermissionService


def _user_has_permission(user_perms: list[str], required: str) -> bool:
    return EffectivePermissionService.matches(user_perms, required)


class ModuleAccessService:
    def __init__(
        self,
        *,
        module_service: ModuleEntitlementService,
        permission_service: PermissionService,
        access_control: AccessControlService,
    ) -> None:
        self._modules = module_service
        self._permissions = permission_service
        self._access_control = access_control

    async def _module_enabled(self, *, company_id: str, module_code: str) -> bool:
        if not await self._access_control.is_module_api_enabled(
            company_id=company_id, module_code=module_code
        ):
            return False
        entitlements = await self._modules.list_entitlements(company_id=company_id)
        enabled_map = {e["moduleCode"]: e["enabled"] for e in entitlements}
        return enabled_map.get(module_code, True)

    async def assert_access(
        self, *, company_id: str, user_id: str, module_code: str
    ) -> None:
        code = module_code.strip().lower()
        await self._access_control.assert_module_api_enabled(
            company_id=company_id, module_code=code
        )
        await self._modules.assert_enabled(company_id=company_id, module_code=code)
        # Write gate: use the write-only permission set (read-tier permissions do
        # not authorize mutating routes). Fail closed on an unknown module code so
        # a typo/new module can never silently authorize every member.
        required = MODULE_WRITE_PERMISSIONS.get(code)
        if required is None:
            raise ForbiddenError(f"Unknown module: {module_code}")
        await self._permissions.assert_any_allowed(
            company_id=company_id, user_id=user_id, permissions=required
        )

    async def matrix_for_user(
        self, *, company_id: str, user_id: str
    ) -> list[dict[str, Any]]:
        entitlements = await self._modules.list_entitlements(company_id=company_id)
        enabled_map = {e["moduleCode"]: e["enabled"] for e in entitlements}
        module_config = await self._access_control.list_module_config(company_id=company_id)
        config_map = {m["moduleCode"]: m for m in module_config}
        user_perms = await self._permissions.permissions_for(
            company_id=company_id, user_id=user_id
        )
        rows: list[dict[str, Any]] = []
        for code in sorted(ALL_MODULE_CODES):
            required = MODULE_PERMISSION_MATRIX.get(code, ())
            has_perm = (
                not required
                or any(_user_has_permission(user_perms, p) for p in required)
            )
            entitled = enabled_map.get(code, True)
            cfg = config_map.get(code, {})
            company_enabled = cfg.get("enabled", True)
            enabled = entitled and company_enabled
            rows.append(
                {
                    "moduleCode": code,
                    "enabled": enabled,
                    "sidebarVisible": cfg.get("sidebarVisible", True) and enabled,
                    "routesEnabled": cfg.get("routesEnabled", True) and enabled,
                    "apiEnabled": cfg.get("apiEnabled", True) and enabled,
                    "reportsEnabled": cfg.get("reportsEnabled", True) and enabled,
                    "widgetsEnabled": cfg.get("widgetsEnabled", True) and enabled,
                    "requiredPermissions": list(required),
                    "userHasPermission": has_perm,
                    "canAccess": enabled and has_perm,
                }
            )
        return rows

    async def assert_list_read(
        self, *, company_id: str, user_id: str, module_code: str
    ) -> None:
        """Module enabled plus a list/read permission — P25."""

        code = module_code.strip().lower()
        await self._access_control.assert_module_api_enabled(
            company_id=company_id, module_code=code
        )
        await self._modules.assert_enabled(company_id=company_id, module_code=code)
        required = MODULE_LIST_READ_PERMISSIONS.get(code)
        if required:
            await self._permissions.assert_any_allowed(
                company_id=company_id,
                user_id=user_id,
                permissions=required,
            )

    async def assert_reports(
        self, *, company_id: str, user_id: str, module_code: str
    ) -> None:
        code = module_code.strip().lower()
        await self._access_control.assert_module_reports_enabled(
            company_id=company_id, module_code=code
        )
        await self._modules.assert_enabled(company_id=company_id, module_code=code)
        required = MODULE_LIST_READ_PERMISSIONS.get(code)
        if required:
            await self._permissions.assert_any_allowed(
                company_id=company_id,
                user_id=user_id,
                permissions=required,
            )
