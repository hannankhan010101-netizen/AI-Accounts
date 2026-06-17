"""Role CRUD for tenant RBAC — P25 / RBAC v2."""

from __future__ import annotations

from typing import Any

from prisma_generated import Prisma
from prisma_generated.fields import Json
from prisma_generated.models import Role

from app.repositories.role_permission_repository import RolePermissionRepository


class RoleRepository:
    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client
        self._role_permissions = RolePermissionRepository(prisma_client)

    def _role_dict(self, row: Role, permissions: list[str] | None = None) -> dict[str, Any]:
        perms = permissions
        if perms is None:
            perms = row.permissions if isinstance(row.permissions, list) else []
        return {
            "id": row.id,
            "name": row.name,
            "code": row.code,
            "description": row.description,
            "parentRoleId": row.parentRoleId,
            "isSystem": row.isSystem,
            "isTemplate": row.isTemplate,
            "sortOrder": row.sortOrder,
            "permissions": perms,
        }

    async def get_role(self, *, company_id: str, role_id: str) -> Role | None:
        row = await self._db.role.find_unique(where={"id": role_id})
        if row is None or row.companyId != company_id:
            return None
        return row

    async def get_role_payload(self, *, company_id: str, role_id: str) -> dict[str, Any] | None:
        row = await self.get_role(company_id=company_id, role_id=role_id)
        if row is None:
            return None
        perms = await self._role_permissions.list_codes_for_role(role_id=role_id)
        if not perms and isinstance(row.permissions, list):
            perms = [str(p) for p in row.permissions]
        return self._role_dict(row, perms)

    async def _assert_not_circular(self, *, role_id: str, parent_role_id: str | None) -> None:
        if not parent_role_id or parent_role_id == role_id:
            if parent_role_id == role_id:
                raise ValueError("Role cannot be its own parent")
            return
        visited = {role_id}
        current = parent_role_id
        while current:
            if current in visited:
                raise ValueError("Circular role hierarchy detected")
            visited.add(current)
            parent = await self._db.role.find_unique(where={"id": current})
            if parent is None:
                break
            current = parent.parentRoleId

    async def create_role(
        self,
        *,
        company_id: str,
        name: str,
        permissions: list[str],
        description: str | None = None,
        parent_role_id: str | None = None,
        code: str | None = None,
        is_system: bool = False,
        is_template: bool = False,
        sort_order: int = 0,
    ) -> Role:
        existing = await self._db.role.find_first(
            where={"companyId": company_id, "name": name.strip()},
        )
        if existing is not None:
            raise ValueError("Role name already exists")
        if code:
            dup_code = await self._db.role.find_first(
                where={"companyId": company_id, "code": code.strip()},
            )
            if dup_code is not None:
                raise ValueError("Role code already exists")
        if parent_role_id:
            parent = await self.get_role(company_id=company_id, role_id=parent_role_id)
            if parent is None:
                raise ValueError("Parent role not found")

        row = await self._db.role.create(
            data={
                "companyId": company_id,
                "name": name.strip(),
                "code": code.strip() if code else None,
                "description": description,
                "parentRoleId": parent_role_id,
                "isSystem": is_system,
                "isTemplate": is_template,
                "sortOrder": sort_order,
                "permissions": Json(permissions),
            },
        )
        await self._role_permissions.sync_dual_write(role_id=row.id, codes=permissions)
        return row

    async def create_from_template(
        self,
        *,
        company_id: str,
        template: dict[str, Any],
        name: str | None = None,
    ) -> Role:
        role_name = (name or str(template["name"])).strip()
        perms = [str(p) for p in template.get("permissions", [])]
        return await self.create_role(
            company_id=company_id,
            name=role_name,
            permissions=perms,
            description=str(template.get("description") or ""),
            code=None,
            is_system=False,
            is_template=False,
            sort_order=int(template.get("sortOrder", 0)),
        )

    async def update_role(
        self,
        *,
        company_id: str,
        role_id: str,
        name: str | None = None,
        permissions: list[str] | None = None,
        description: str | None = None,
        parent_role_id: str | None = None,
        _unset_parent: bool = False,
    ) -> Role:
        row = await self.get_role(company_id=company_id, role_id=role_id)
        if row is None:
            raise ValueError("Role not found")
        if row.isSystem and name and name != row.name:
            raise ValueError("Cannot rename a system role")
        data: dict[str, Any] = {}
        if name is not None:
            dup = await self._db.role.find_first(
                where={
                    "companyId": company_id,
                    "name": name.strip(),
                    "id": {"not": role_id},
                },
            )
            if dup is not None:
                raise ValueError("Role name already exists")
            data["name"] = name.strip()
        if description is not None:
            data["description"] = description
        if _unset_parent:
            data["parentRoleId"] = None
        elif parent_role_id is not None:
            await self._assert_not_circular(role_id=role_id, parent_role_id=parent_role_id)
            parent = await self.get_role(company_id=company_id, role_id=parent_role_id)
            if parent is None:
                raise ValueError("Parent role not found")
            data["parentRoleId"] = parent_role_id
        if permissions is not None:
            data["permissions"] = Json(permissions)
        updated = await self._db.role.update(where={"id": role_id}, data=data)
        if permissions is not None:
            await self._role_permissions.sync_dual_write(role_id=role_id, codes=permissions)
        return updated

    async def delete_role(self, *, company_id: str, role_id: str) -> None:
        row = await self.get_role(company_id=company_id, role_id=role_id)
        if row is None:
            raise ValueError("Role not found")
        if row.isSystem:
            raise ValueError("Cannot delete a system role")
        mem_count = await self._db.membershiprole.count(where={"roleId": role_id})
        legacy_count = await self._db.companymembership.count(
            where={"companyId": company_id, "roleId": role_id},
        )
        if mem_count > 0 or legacy_count > 0:
            raise ValueError("Role is assigned to users; reassign them first")
        await self._db.role.delete(where={"id": role_id})

    async def clone_role(
        self,
        *,
        company_id: str,
        role_id: str,
        name: str | None = None,
    ) -> Role:
        row = await self.get_role(company_id=company_id, role_id=role_id)
        if row is None:
            raise ValueError("Role not found")
        perms = await self._role_permissions.list_codes_for_role(role_id=role_id)
        if not perms and isinstance(row.permissions, list):
            perms = [str(p) for p in row.permissions]
        base = (name or f"{row.name} (Copy)").strip()
        candidate = base
        suffix = 2
        while True:
            dup = await self._db.role.find_first(
                where={"companyId": company_id, "name": candidate},
            )
            if dup is None:
                break
            candidate = f"{base} {suffix}"
            suffix += 1
        return await self.create_role(
            company_id=company_id,
            name=candidate,
            permissions=perms,
            description=row.description,
            parent_role_id=row.parentRoleId,
        )

    async def list_roles_for_export(self, *, company_id: str) -> list[dict[str, Any]]:
        rows = await self._db.role.find_many(
            where={"companyId": company_id},
            order={"sortOrder": "asc"},
        )
        out: list[dict[str, Any]] = []
        for r in rows:
            perms = await self._role_permissions.list_codes_for_role(role_id=r.id)
            if not perms and isinstance(r.permissions, list):
                perms = [str(p) for p in r.permissions]
            out.append(self._role_dict(r, perms))
        return out

    async def list_roles(self, *, company_id: str) -> list[dict[str, Any]]:
        return await self.list_roles_for_export(company_id=company_id)

    async def clone_roles_batch(
        self,
        *,
        company_id: str,
        role_ids: list[str],
        name_suffix: str | None = None,
    ) -> list[Role]:
        suffix = (name_suffix or " (Copy)").strip()
        created: list[Role] = []
        for role_id in role_ids:
            source = await self.get_role(company_id=company_id, role_id=role_id)
            if source is None:
                raise ValueError(f"Role not found: {role_id}")
            row = await self.clone_role(
                company_id=company_id,
                role_id=role_id,
                name=f"{source.name}{suffix}",
            )
            created.append(row)
        return created

    async def import_roles(
        self,
        *,
        company_id: str,
        roles: list[dict[str, Any]],
        skip_existing: bool = True,
    ) -> dict[str, list[dict[str, Any]]]:
        created: list[dict[str, Any]] = []
        skipped: list[dict[str, Any]] = []
        for entry in roles:
            name = str(entry.get("name", "")).strip()
            if not name:
                skipped.append({"name": "", "reason": "empty_name"})
                continue
            perms_raw = entry.get("permissions", [])
            permissions = [str(p) for p in perms_raw] if isinstance(perms_raw, list) else []
            existing = await self._db.role.find_first(
                where={"companyId": company_id, "name": name},
            )
            if existing is not None:
                if skip_existing:
                    skipped.append({"name": name, "reason": "exists", "id": existing.id})
                    continue
                raise ValueError(f"Role name already exists: {name}")
            row = await self.create_role(
                company_id=company_id,
                name=name,
                permissions=permissions,
                description=str(entry.get("description") or "") or None,
            )
            created.append(self._role_dict(row, permissions))
        return {"created": created, "skipped": skipped}

    async def preview_import_roles(
        self,
        *,
        company_id: str,
        roles: list[dict[str, Any]],
        skip_existing: bool = True,
    ) -> dict[str, list[dict[str, Any]]]:
        would_create: list[dict[str, Any]] = []
        would_skip: list[dict[str, Any]] = []
        for entry in roles:
            name = str(entry.get("name", "")).strip()
            if not name:
                would_skip.append({"name": "", "reason": "empty_name"})
                continue
            perms_raw = entry.get("permissions", [])
            permissions = [str(p) for p in perms_raw] if isinstance(perms_raw, list) else []
            existing = await self._db.role.find_first(
                where={"companyId": company_id, "name": name},
            )
            if existing is not None:
                if skip_existing:
                    would_skip.append({"name": name, "reason": "exists", "id": existing.id})
                    continue
                would_skip.append({"name": name, "reason": "would_fail_duplicate"})
                continue
            would_create.append({"name": name, "permissions": permissions})
        return {"wouldCreate": would_create, "wouldSkip": would_skip}
