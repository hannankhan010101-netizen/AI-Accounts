"""Role ↔ permission join table — RBAC v2."""

from __future__ import annotations

from prisma_generated import Prisma


class RolePermissionRepository:
    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_codes_for_role(self, *, role_id: str) -> list[str]:
        rows = await self._db.rolepermission.find_many(
            where={"roleId": role_id, "granted": True},
        )
        return [r.permissionCode for r in rows]

    async def replace_for_role(self, *, role_id: str, codes: list[str]) -> None:
        await self._db.rolepermission.delete_many(where={"roleId": role_id})
        unique = sorted(set(codes))
        if not unique:
            return
        await self._db.rolepermission.create_many(
            data=[{"roleId": role_id, "permissionCode": c, "granted": True} for c in unique],
            skipDuplicates=True,
        )

    async def sync_dual_write(self, *, role_id: str, codes: list[str]) -> None:
        """Keep role_permissions and legacy JSON in sync."""
        from prisma_generated.fields import Json

        await self.replace_for_role(role_id=role_id, codes=codes)
        await self._db.role.update(
            where={"id": role_id},
            data={"permissions": Json(codes)},
        )
