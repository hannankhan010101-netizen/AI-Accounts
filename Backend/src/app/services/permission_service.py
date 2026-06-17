"""Tenant RBAC — Sprint 9 / RBAC v2."""

from __future__ import annotations

from app.core.exceptions import ForbiddenError
from app.services.access_control_service import AccessControlService
from app.services.effective_permission_service import EffectivePermissionService


class PermissionService:
    """Check membership role permissions for the active company."""

    def __init__(
        self,
        *,
        effective_permissions: EffectivePermissionService,
        access_control: AccessControlService,
    ) -> None:
        self._effective = effective_permissions
        self._access_control = access_control

    async def permissions_for(
        self, *, company_id: str, user_id: str
    ) -> list[str]:
        perms = await self._effective.permissions_for_user(
            company_id=company_id, user_id=user_id
        )
        disabled = await self._access_control.disabled_modules(company_id=company_id)
        return self._effective.filter_by_module(perms, disabled)

    async def assert_membership_has_role(self, *, company_id: str, user_id: str) -> None:
        """Deny when the user has no role permissions (P0 deny-by-default)."""

        perms = await self.permissions_for(company_id=company_id, user_id=user_id)
        if not perms:
            raise ForbiddenError(
                "No role assigned for this company. Ask an administrator to assign a role."
            )

    async def assert_allowed(
        self, *, company_id: str, user_id: str, permission: str
    ) -> None:
        perms = await self.permissions_for(company_id=company_id, user_id=user_id)
        if not perms:
            raise ForbiddenError(
                "No role assigned for this company. Ask an administrator to assign a role."
            )
        if not self._effective.matches(perms, permission):
            raise ForbiddenError(f"Missing permission: {permission}")

    async def assert_any_allowed(
        self, *, company_id: str, user_id: str, permissions: tuple[str, ...]
    ) -> None:
        """Pass when the user has any one of the listed permissions (or ``*``)."""

        perms = await self.permissions_for(company_id=company_id, user_id=user_id)
        if not perms:
            raise ForbiddenError(
                "No role assigned for this company. Ask an administrator to assign a role."
            )
        if "*" in perms:
            return
        for required in permissions:
            if self._effective.matches(perms, required):
                return
        raise ForbiddenError(
            f"Missing one of required permissions: {', '.join(permissions)}"
        )
