"""Effective permission resolution — multi-role union + hierarchy."""

from __future__ import annotations

from prisma_generated import Prisma

from app.repositories.membership_role_repository import MembershipRoleRepository
from app.repositories.role_permission_repository import RolePermissionRepository


class EffectivePermissionService:
    def __init__(
        self,
        *,
        prisma_client: Prisma,
        role_permissions: RolePermissionRepository,
        membership_roles: MembershipRoleRepository,
    ) -> None:
        self._db = prisma_client
        self._role_permissions = role_permissions
        self._membership_roles = membership_roles

    async def permissions_for_role(self, *, role_id: str, _visited: set[str] | None = None) -> list[str]:
        visited = _visited or set()
        if role_id in visited:
            return []
        visited.add(role_id)

        role = await self._db.role.find_unique(where={"id": role_id})
        if role is None:
            return []

        codes = await self._role_permissions.list_codes_for_role(role_id=role_id)
        if not codes and isinstance(role.permissions, list):
            codes = [str(c) for c in role.permissions]

        if role.parentRoleId:
            parent = await self.permissions_for_role(role_id=role.parentRoleId, _visited=visited)
            codes = sorted(set(parent) | set(codes))

        return codes

    async def permissions_for_membership(self, *, membership_id: str) -> list[str]:
        role_ids = await self._membership_roles.list_role_ids(membership_id=membership_id)
        if not role_ids:
            row = await self._db.companymembership.find_unique(where={"id": membership_id})
            if row and row.roleId:
                role_ids = [row.roleId]
        merged: set[str] = set()
        for rid in role_ids:
            merged.update(await self.permissions_for_role(role_id=rid))
        return sorted(merged)

    async def permissions_for_user(self, *, company_id: str, user_id: str) -> list[str]:
        row = await self._db.companymembership.find_unique(
            where={"companyId_userId": {"companyId": company_id, "userId": user_id}},
        )
        if row is None:
            return []
        return await self.permissions_for_membership(membership_id=row.id)

    @staticmethod
    def matches(perms: list[str], permission: str) -> bool:
        if "*" in perms:
            return True
        if permission in perms:
            return True
        parts = permission.split(".")
        for i in range(len(parts) - 1, 0, -1):
            wc = ".".join(parts[:i]) + ".*"
            if wc in perms:
                return True
        return False

    @staticmethod
    def filter_by_module(perms: list[str], disabled_modules: set[str]) -> list[str]:
        if "*" in perms:
            return perms
        out: list[str] = []
        for code in perms:
            module = code.split(".", 1)[0]
            if module in disabled_modules:
                continue
            out.append(code)
        return out
