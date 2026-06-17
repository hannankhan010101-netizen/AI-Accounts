"""Access control: module config, field security, data scope — RBAC v2."""

from __future__ import annotations

from typing import Any

from prisma_generated import Prisma

from app.constants.module_codes import ALL_MODULE_CODES
from app.constants.permission_registry import FIELD_SECURITY_KEYS


class AccessControlService:
    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_module_config(self, *, company_id: str) -> list[dict[str, Any]]:
        rows = await self._db.companymoduleconfig.find_many(
            where={"companyId": company_id},
            order={"moduleCode": "asc"},
        )
        by_code = {r.moduleCode: r for r in rows}
        out: list[dict[str, Any]] = []
        for code in sorted(ALL_MODULE_CODES):
            row = by_code.get(code)
            out.append(
                {
                    "moduleCode": code,
                    "enabled": row.enabled if row else True,
                    "sidebarVisible": row.sidebarVisible if row else True,
                    "routesEnabled": row.routesEnabled if row else True,
                    "apiEnabled": row.apiEnabled if row else True,
                    "reportsEnabled": row.reportsEnabled if row else True,
                    "widgetsEnabled": row.widgetsEnabled if row else True,
                }
            )
        return out

    async def replace_module_config(
        self, *, company_id: str, modules: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        for entry in modules:
            code = str(entry.get("moduleCode", "")).strip()
            if not code:
                continue
            await self._db.companymoduleconfig.upsert(
                where={
                    "companyId_moduleCode": {"companyId": company_id, "moduleCode": code},
                },
                data={
                    "create": {
                        "companyId": company_id,
                        "moduleCode": code,
                        "enabled": bool(entry.get("enabled", True)),
                        "sidebarVisible": bool(entry.get("sidebarVisible", True)),
                        "routesEnabled": bool(entry.get("routesEnabled", True)),
                        "apiEnabled": bool(entry.get("apiEnabled", True)),
                        "reportsEnabled": bool(entry.get("reportsEnabled", True)),
                        "widgetsEnabled": bool(entry.get("widgetsEnabled", True)),
                    },
                    "update": {
                        "enabled": bool(entry.get("enabled", True)),
                        "sidebarVisible": bool(entry.get("sidebarVisible", True)),
                        "routesEnabled": bool(entry.get("routesEnabled", True)),
                        "apiEnabled": bool(entry.get("apiEnabled", True)),
                        "reportsEnabled": bool(entry.get("reportsEnabled", True)),
                        "widgetsEnabled": bool(entry.get("widgetsEnabled", True)),
                    },
                },
            )
        return await self.list_module_config(company_id=company_id)

    async def disabled_modules(self, *, company_id: str) -> set[str]:
        rows = await self._db.companymoduleconfig.find_many(
            where={"companyId": company_id, "enabled": False},
        )
        return {r.moduleCode for r in rows}

    async def is_module_api_enabled(self, *, company_id: str, module_code: str) -> bool:
        row = await self._db.companymoduleconfig.find_unique(
            where={
                "companyId_moduleCode": {"companyId": company_id, "moduleCode": module_code},
            },
        )
        if row is not None and (not row.enabled or not row.apiEnabled):
            return False
        return True

    async def assert_module_api_enabled(self, *, company_id: str, module_code: str) -> None:
        from app.core.exceptions import ForbiddenError

        row = await self._db.companymoduleconfig.find_unique(
            where={
                "companyId_moduleCode": {"companyId": company_id, "moduleCode": module_code},
            },
        )
        if row is not None and (not row.enabled or not row.apiEnabled):
            raise ForbiddenError(f"Module '{module_code}' is disabled for this company.")

    async def assert_module_reports_enabled(
        self, *, company_id: str, module_code: str
    ) -> None:
        from app.core.exceptions import ForbiddenError

        row = await self._db.companymoduleconfig.find_unique(
            where={
                "companyId_moduleCode": {"companyId": company_id, "moduleCode": module_code},
            },
        )
        if row is not None and (
            not row.enabled or not row.apiEnabled or not row.reportsEnabled
        ):
            raise ForbiddenError(
                f"Reports for module '{module_code}' are disabled for this company."
            )

    async def assert_module_widgets_enabled(
        self, *, company_id: str, module_code: str
    ) -> None:
        from app.core.exceptions import ForbiddenError

        row = await self._db.companymoduleconfig.find_unique(
            where={
                "companyId_moduleCode": {"companyId": company_id, "moduleCode": module_code},
            },
        )
        if row is not None and (
            not row.enabled or not row.apiEnabled or not row.widgetsEnabled
        ):
            raise ForbiddenError(
                f"Dashboard widgets for module '{module_code}' are disabled for this company."
            )

    async def list_field_policies(
        self, *, company_id: str, role_id: str | None = None
    ) -> list[dict[str, Any]]:
        where: dict[str, Any] = {"companyId": company_id}
        if role_id:
            where["roleId"] = role_id
        rows = await self._db.fieldsecuritypolicy.find_many(where=where)
        return [
            {
                "id": r.id,
                "roleId": r.roleId,
                "fieldKey": r.fieldKey,
                "accessLevel": r.accessLevel,
            }
            for r in rows
        ]

    async def replace_field_policies(
        self,
        *,
        company_id: str,
        role_id: str,
        policies: list[dict[str, str]],
    ) -> list[dict[str, Any]]:
        valid_keys = {f["key"] for f in FIELD_SECURITY_KEYS}
        await self._db.fieldsecuritypolicy.delete_many(
            where={"companyId": company_id, "roleId": role_id},
        )
        for entry in policies:
            key = str(entry.get("fieldKey", "")).strip()
            level = str(entry.get("accessLevel", "view")).strip()
            if key not in valid_keys or level not in ("view", "edit", "hidden"):
                continue
            await self._db.fieldsecuritypolicy.create(
                data={
                    "companyId": company_id,
                    "roleId": role_id,
                    "fieldKey": key,
                    "accessLevel": level,
                },
            )
        return await self.list_field_policies(company_id=company_id, role_id=role_id)

    async def field_access_for_roles(
        self, *, company_id: str, role_ids: list[str]
    ) -> dict[str, str]:
        """Most permissive wins across roles: edit > view > hidden."""
        rank = {"hidden": 0, "view": 1, "edit": 2}
        merged: dict[str, str] = {}
        for role_id in role_ids:
            rows = await self._db.fieldsecuritypolicy.find_many(
                where={"companyId": company_id, "roleId": role_id},
            )
            for row in rows:
                current = merged.get(row.fieldKey, "hidden")
                if rank.get(row.accessLevel, 0) > rank.get(current, 0):
                    merged[row.fieldKey] = row.accessLevel
        return merged

    async def list_data_scope(self, *, company_id: str, membership_id: str) -> list[dict[str, str]]:
        rows = await self._db.userdataassignment.find_many(
            where={"companyId": company_id, "membershipId": membership_id},
        )
        return [{"scopeType": r.scopeType, "scopeId": r.scopeId} for r in rows]

    async def replace_data_scope(
        self,
        *,
        company_id: str,
        membership_id: str,
        assignments: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        await self._db.userdataassignment.delete_many(
            where={"companyId": company_id, "membershipId": membership_id},
        )
        for entry in assignments:
            scope_type = str(entry.get("scopeType", "")).strip()
            scope_id = str(entry.get("scopeId", "")).strip()
            if not scope_type or not scope_id:
                continue
            await self._db.userdataassignment.create(
                data={
                    "companyId": company_id,
                    "membershipId": membership_id,
                    "scopeType": scope_type,
                    "scopeId": scope_id,
                },
            )
        return await self.list_data_scope(company_id=company_id, membership_id=membership_id)

    async def allowed_scope_ids(
        self, *, company_id: str, membership_id: str, scope_type: str
    ) -> list[str] | None:
        rows = await self._db.userdataassignment.find_many(
            where={
                "companyId": company_id,
                "membershipId": membership_id,
                "scopeType": scope_type,
            },
        )
        if not rows:
            return None
        return [r.scopeId for r in rows]
