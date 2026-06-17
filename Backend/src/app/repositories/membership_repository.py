"""Company membership + role lookups for RBAC — Sprint 9."""

from __future__ import annotations

from typing import Any

from prisma_generated import Prisma

from app.repositories.membership_role_repository import MembershipRoleRepository


class MembershipRepository:
    """Resolve a user's role permissions within a company."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client
        self._membership_roles = MembershipRoleRepository(prisma_client)

    async def get_membership(
        self, *, company_id: str, user_id: str
    ) -> dict[str, Any] | None:
        row = await self._db.companymembership.find_unique(
            where={"companyId_userId": {"companyId": company_id, "userId": user_id}},
            include={"role": True, "user": True},
        )
        if row is None:
            return None
        roles = await self._membership_roles.list_roles_for_membership(
            membership_id=row.id
        )
        role_ids = [r["roleId"] for r in roles]
        if not role_ids and row.roleId:
            role_ids = [row.roleId]
            roles = [
                {
                    "roleId": row.roleId,
                    "roleName": row.role.name if row.role else None,
                    "roleCode": row.role.code if row.role else None,
                    "isPrimary": True,
                }
            ]
        perms: list[str] = []
        if row.role and isinstance(row.role.permissions, list):
            perms = [str(p) for p in row.role.permissions]
        return {
            "id": row.id,
            "userId": row.userId,
            "companyId": row.companyId,
            "roleId": row.roleId,
            "roleIds": role_ids,
            "roles": roles,
            "roleName": row.role.name if row.role else None,
            "permissions": perms,
            "ipAllowlist": row.ipAllowlist,
            "user": {
                "id": row.user.id,
                "email": row.user.email,
                "firstName": row.user.firstName,
                "lastName": row.user.lastName,
                "isActive": row.user.isActive,
                "emailVerified": row.user.emailVerified,
            },
        }

    async def list_members(
        self,
        *,
        company_id: str,
        page: int = 1,
        page_size: int = 25,
        search: str | None = None,
        is_active: bool | None = None,
        role_id: str | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        """Paginated company members with optional filters — P33/P34/P39."""

        page = max(1, page)
        page_size = min(max(1, page_size), 100)
        skip = (page - 1) * page_size
        if user_id:
            where: dict[str, Any] = {"companyId": company_id, "userId": user_id}
            if role_id:
                where["roleId"] = role_id
            if is_active is not None:
                where["user"] = {"isActive": is_active}
            total = await self._db.companymembership.count(where=where)
            rows = await self._db.companymembership.find_many(
                where=where,
                include={"role": True, "user": True},
                order={"createdAt": "asc"},
                skip=skip,
                take=page_size,
            )
            items = self._members_to_dicts(rows)
            return {
                "items": items,
                "page": page,
                "pageSize": page_size,
                "total": total,
            }
        user_where: dict[str, Any] = {}
        if is_active is not None:
            user_where["isActive"] = is_active
        term = search.strip() if search else ""
        if term:
            where = {
                "companyId": company_id,
                "OR": [
                    {
                        "user": {
                            **user_where,
                            "email": {"contains": term, "mode": "insensitive"},
                        }
                    },
                    {
                        "user": {
                            **user_where,
                            "firstName": {"contains": term, "mode": "insensitive"},
                        }
                    },
                    {
                        "user": {
                            **user_where,
                            "lastName": {"contains": term, "mode": "insensitive"},
                        }
                    },
                ],
            }
        elif user_where:
            where = {"companyId": company_id, "user": user_where}
        else:
            where = {"companyId": company_id}
        if role_id:
            where["roleId"] = role_id
        total = await self._db.companymembership.count(where=where)
        rows = await self._db.companymembership.find_many(
            where=where,
            include={"role": True, "user": True},
            order={"createdAt": "asc"},
            skip=skip,
            take=page_size,
        )
        items = self._members_to_dicts(rows)
        items = await self._enrich_membership_roles(items)
        return {
            "items": items,
            "page": page,
            "pageSize": page_size,
            "total": total,
        }

    async def _enrich_membership_roles(
        self, items: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        membership_ids = [str(item["id"]) for item in items]
        roles_map = await self._membership_roles.list_roles_by_membership_ids(
            membership_ids=membership_ids
        )
        for item in items:
            roles = roles_map.get(str(item["id"]), [])
            if roles:
                item["roles"] = roles
                item["roleIds"] = [r["roleId"] for r in roles]
                primary = next((r for r in roles if r.get("isPrimary")), roles[0])
                item["roleId"] = primary["roleId"]
                item["roleName"] = primary.get("roleName")
            elif item.get("roleId"):
                item["roleIds"] = [item["roleId"]]
        return items

    async def list_members_all(self, *, company_id: str) -> list[dict[str, Any]]:
        rows = await self._db.companymembership.find_many(
            where={"companyId": company_id},
            include={"role": True, "user": True},
            order={"createdAt": "asc"},
        )
        return await self._enrich_membership_roles(self._members_to_dicts(rows))

    def _members_to_dicts(self, rows: list[Any]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for row in rows:
            perms: list[str] = []
            if row.role and isinstance(row.role.permissions, list):
                perms = [str(p) for p in row.role.permissions]
            out.append(
                {
                    "id": row.id,
                    "userId": row.userId,
                    "roleId": row.roleId,
                    "roleName": row.role.name if row.role else None,
                    "permissions": perms,
                    "email": row.user.email,
                    "firstName": row.user.firstName,
                    "lastName": row.user.lastName,
                    "isActive": row.user.isActive,
                    "emailVerified": row.user.emailVerified,
                    "ipAllowlist": row.ipAllowlist,
                }
            )
        return out

    async def list_roles(self, *, company_id: str) -> list[dict[str, Any]]:
        rows = await self._db.role.find_many(
            where={"companyId": company_id},
            order={"name": "asc"},
        )
        return [
            {
                "id": r.id,
                "name": r.name,
                "permissions": r.permissions if isinstance(r.permissions, list) else [],
            }
            for r in rows
        ]

    async def assign_role(
        self,
        *,
        company_id: str,
        user_id: str,
        role_id: str,
    ) -> dict[str, Any]:
        role = await self._db.role.find_unique(where={"id": role_id})
        if role is None or role.companyId != company_id:
            raise ValueError("Role not found in this company")

        row = await self._db.companymembership.find_unique(
            where={"companyId_userId": {"companyId": company_id, "userId": user_id}},
            include={"role": True, "user": True},
        )
        if row is None:
            raise ValueError("User is not a member of this company")

        updated = await self._db.companymembership.update(
            where={"id": row.id},
            data={"roleId": role_id},
            include={"role": True, "user": True},
        )
        await self._membership_roles.ensure_primary_from_legacy(
            membership_id=row.id, role_id=role_id
        )
        perms: list[str] = []
        if updated.role and isinstance(updated.role.permissions, list):
            perms = [str(p) for p in updated.role.permissions]
        return {
            "id": updated.id,
            "userId": updated.userId,
            "roleId": updated.roleId,
            "roleName": updated.role.name if updated.role else None,
            "permissions": perms,
            "email": updated.user.email,
        }

    async def invite_member(
        self,
        *,
        company_id: str,
        email: str,
        first_name: str,
        last_name: str,
        role_id: str,
        password_hash: str,
    ) -> dict[str, Any]:
        """Create user if needed, add company membership with role — P27."""

        normalized = email.strip().lower()
        role = await self._db.role.find_unique(where={"id": role_id})
        if role is None or role.companyId != company_id:
            raise ValueError("Role not found in this company")

        user = await self._db.user.find_unique(where={"email": normalized})
        user_created = False
        if user is None:
            user = await self._db.user.create(
                data={
                    "email": normalized,
                    "passwordHash": password_hash,
                    "firstName": first_name,
                    "lastName": last_name,
                    "emailVerified": False,
                }
            )
            user_created = True

        existing = await self._db.companymembership.find_unique(
            where={
                "companyId_userId": {"companyId": company_id, "userId": user.id}
            },
        )
        if existing is not None:
            raise ValueError("User is already a member of this company")

        row = await self._db.companymembership.create(
            data={
                "companyId": company_id,
                "userId": user.id,
                "isDefault": False,
                "roleId": role_id,
            },
            include={"role": True, "user": True},
        )
        await self._membership_roles.ensure_primary_from_legacy(
            membership_id=row.id, role_id=role_id
        )
        perms: list[str] = []
        if row.role and isinstance(row.role.permissions, list):
            perms = [str(p) for p in row.role.permissions]
        return {
            "id": row.id,
            "userId": row.userId,
            "roleId": row.roleId,
            "roleName": row.role.name if row.role else None,
            "permissions": perms,
            "email": row.user.email,
            "firstName": row.user.firstName,
            "lastName": row.user.lastName,
            "isActive": row.user.isActive,
            "userCreated": user_created,
        }

    async def reinvite_member(
        self,
        *,
        company_id: str,
        user_id: str,
        role_id: str,
    ) -> dict[str, Any]:
        """Re-add an existing user after membership was revoked — P34."""

        role = await self._db.role.find_unique(where={"id": role_id})
        if role is None or role.companyId != company_id:
            raise ValueError("Role not found in this company")

        user = await self._db.user.find_unique(where={"id": user_id})
        if user is None:
            raise ValueError("User not found")

        existing = await self._db.companymembership.find_unique(
            where={"companyId_userId": {"companyId": company_id, "userId": user_id}},
        )
        if existing is not None:
            raise ValueError("User is already a member of this company")

        row = await self._db.companymembership.create(
            data={
                "companyId": company_id,
                "userId": user_id,
                "isDefault": False,
                "roleId": role_id,
            },
            include={"role": True, "user": True},
        )
        perms: list[str] = []
        if row.role and isinstance(row.role.permissions, list):
            perms = [str(p) for p in row.role.permissions]
        return {
            "id": row.id,
            "userId": row.userId,
            "roleId": row.roleId,
            "roleName": row.role.name if row.role else None,
            "permissions": perms,
            "email": row.user.email,
            "firstName": row.user.firstName,
            "lastName": row.user.lastName,
            "isActive": row.user.isActive,
            "reinvited": True,
        }

    async def revoke_membership(
        self,
        *,
        company_id: str,
        user_id: str,
        acting_user_id: str,
    ) -> dict[str, str]:
        """Remove a user from the company — P32."""

        if user_id == acting_user_id:
            raise ValueError("Cannot revoke your own membership")

        row = await self._db.companymembership.find_unique(
            where={"companyId_userId": {"companyId": company_id, "userId": user_id}},
            include={"role": True, "user": True},
        )
        if row is None:
            raise ValueError("User is not a member of this company")

        if row.role and (row.role.code == "super_admin" or row.role.name in ("Super Admin", "Administrator")):
            admin_role = row.role
            admin_count = await self._db.companymembership.count(
                where={"companyId": company_id, "roleId": admin_role.id},
            )
            if admin_count <= 1:
                raise ValueError("Cannot revoke the last Super Admin membership")

        await self._db.companymembership.delete(where={"id": row.id})
        return {
            "userId": user_id,
            "email": row.user.email,
            "revoked": "true",
        }

    async def deactivate_user(
        self,
        *,
        company_id: str,
        user_id: str,
        acting_user_id: str,
    ) -> dict[str, str | bool]:
        """Set user inactive (global login block) — P32."""

        if user_id == acting_user_id:
            raise ValueError("Cannot deactivate your own account")

        row = await self._db.companymembership.find_unique(
            where={"companyId_userId": {"companyId": company_id, "userId": user_id}},
            include={"user": True},
        )
        if row is None:
            raise ValueError("User is not a member of this company")

        updated = await self._db.user.update(
            where={"id": user_id},
            data={"isActive": False},
        )
        return {
            "userId": updated.id,
            "email": updated.email,
            "isActive": updated.isActive,
        }

    async def reactivate_user(
        self,
        *,
        company_id: str,
        user_id: str,
        acting_user_id: str,
    ) -> dict[str, str | bool]:
        """Restore user active flag — P33."""

        row = await self._db.companymembership.find_unique(
            where={"companyId_userId": {"companyId": company_id, "userId": user_id}},
            include={"user": True},
        )
        if row is None:
            raise ValueError("User is not a member of this company")

        updated = await self._db.user.update(
            where={"id": user_id},
            data={"isActive": True},
        )
        return {
            "userId": updated.id,
            "email": updated.email,
            "isActive": updated.isActive,
        }

    async def bulk_assign_role(
        self,
        *,
        company_id: str,
        user_ids: list[str],
        role_id: str,
        acting_user_id: str,
    ) -> dict[str, Any]:
        """Assign the same role to many members — P35."""

        succeeded: list[str] = []
        failed: list[dict[str, str]] = []
        for user_id in user_ids:
            try:
                await self.assign_role(
                    company_id=company_id,
                    user_id=user_id,
                    role_id=role_id,
                )
                succeeded.append(user_id)
            except ValueError as exc:
                failed.append({"userId": user_id, "error": str(exc)})
        return {"succeeded": succeeded, "failed": failed, "roleId": role_id}

    async def bulk_revoke_membership(
        self,
        *,
        company_id: str,
        user_ids: list[str],
        acting_user_id: str,
    ) -> dict[str, Any]:
        """Revoke many members from the company — P35."""

        succeeded: list[str] = []
        failed: list[dict[str, str]] = []
        for user_id in user_ids:
            try:
                await self.revoke_membership(
                    company_id=company_id,
                    user_id=user_id,
                    acting_user_id=acting_user_id,
                )
                succeeded.append(user_id)
            except ValueError as exc:
                failed.append({"userId": user_id, "error": str(exc)})
        return {"succeeded": succeeded, "failed": failed}

    async def count_members(self, *, company_id: str) -> int:
        return await self._db.companymembership.count(where={"companyId": company_id})

    async def update_ip_allowlist(
        self,
        *,
        company_id: str,
        user_id: str,
        ip_allowlist: str | None,
    ) -> dict[str, Any]:
        """Set comma-separated IP allowlist for a membership (empty clears restriction)."""

        row = await self._db.companymembership.find_unique(
            where={"companyId_userId": {"companyId": company_id, "userId": user_id}},
            include={"role": True, "user": True},
        )
        if row is None:
            raise ValueError("User is not a member of this company")

        normalized = (ip_allowlist or "").strip() or None
        updated = await self._db.companymembership.update(
            where={"id": row.id},
            data={"ipAllowlist": normalized},
            include={"role": True, "user": True},
        )
        perms: list[str] = []
        if updated.role and isinstance(updated.role.permissions, list):
            perms = [str(p) for p in updated.role.permissions]
        return {
            "id": updated.id,
            "userId": updated.userId,
            "roleId": updated.roleId,
            "roleName": updated.role.name if updated.role else None,
            "permissions": perms,
            "email": updated.user.email,
            "firstName": updated.user.firstName,
            "lastName": updated.user.lastName,
            "isActive": updated.user.isActive,
            "emailVerified": updated.user.emailVerified,
            "ipAllowlist": updated.ipAllowlist,
        }
