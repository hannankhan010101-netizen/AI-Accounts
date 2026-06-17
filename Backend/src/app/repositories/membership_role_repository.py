"""Multi-role membership assignments — RBAC v2."""

from __future__ import annotations

from typing import Any

from prisma_generated import Prisma


class MembershipRoleRepository:
    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_role_ids(self, *, membership_id: str) -> list[str]:
        rows = await self._db.membershiprole.find_many(
            where={"membershipId": membership_id},
            order={"isPrimary": "desc"},
        )
        return [r.roleId for r in rows]

    async def list_roles_for_membership(self, *, membership_id: str) -> list[dict[str, Any]]:
        rows = await self._db.membershiprole.find_many(
            where={"membershipId": membership_id},
            include={"role": True},
            order={"isPrimary": "desc"},
        )
        return [
            {
                "roleId": r.roleId,
                "roleName": r.role.name if r.role else None,
                "roleCode": r.role.code if r.role else None,
                "isPrimary": r.isPrimary,
            }
            for r in rows
        ]

    async def list_roles_by_membership_ids(
        self, *, membership_ids: list[str]
    ) -> dict[str, list[dict[str, Any]]]:
        if not membership_ids:
            return {}
        rows = await self._db.membershiprole.find_many(
            where={"membershipId": {"in": membership_ids}},
            include={"role": True},
            order={"isPrimary": "desc"},
        )
        out: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            out.setdefault(row.membershipId, []).append(
                {
                    "roleId": row.roleId,
                    "roleName": row.role.name if row.role else None,
                    "roleCode": row.role.code if row.role else None,
                    "isPrimary": row.isPrimary,
                }
            )
        return out

    async def replace_roles(
        self,
        *,
        membership_id: str,
        role_ids: list[str],
        primary_role_id: str | None = None,
    ) -> None:
        if not role_ids:
            raise ValueError("At least one role is required")

        primary = primary_role_id or role_ids[0]
        if primary not in role_ids:
            role_ids = [primary, *role_ids]

        await self._db.membershiprole.delete_many(where={"membershipId": membership_id})
        await self._db.membershiprole.create_many(
            data=[
                {
                    "membershipId": membership_id,
                    "roleId": rid,
                    "isPrimary": rid == primary,
                }
                for rid in role_ids
            ],
        )
        await self._db.companymembership.update(
            where={"id": membership_id},
            data={"roleId": primary},
        )

    async def ensure_primary_from_legacy(self, *, membership_id: str, role_id: str) -> None:
        existing = await self._db.membershiprole.find_first(
            where={"membershipId": membership_id, "roleId": role_id},
        )
        if existing is None:
            await self._db.membershiprole.create(
                data={"membershipId": membership_id, "roleId": role_id, "isPrimary": True},
            )
