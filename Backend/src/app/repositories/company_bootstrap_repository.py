"""Default rows created alongside a new tenant."""

from __future__ import annotations

from prisma_generated import Prisma
from prisma_generated.fields import Json

from app.constants.default_chart_of_accounts import DEFAULT_POSTING_DEFAULTS
from app.constants.role_templates import ROLE_TEMPLATES
from app.repositories.coa_repository import CoaRepository
from app.repositories.role_permission_repository import RolePermissionRepository
from app.repositories.smart_settings_repository import SmartSettingsRepository


class CompanyBootstrapRepository:
    """Insert Smart Settings, Business Info, tax shell, lock settings, and RBAC templates."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client
        self._role_permissions = RolePermissionRepository(prisma_client)
        self._coa = CoaRepository(prisma_client)
        self._smart_settings = SmartSettingsRepository(prisma_client)

    async def create_phase1_defaults(self, *, company_id: str) -> None:
        """
        Seed empty configuration documents required before operational vouchers.

        Idempotent skips are not implemented; call once per new company only.
        """

        await self._db.smartsettings.create(
            data={"companyId": company_id, "payload": Json({})},
        )
        await self._db.businessinformation.create(
            data={"companyId": company_id},
        )
        await self._db.lockdatesettings.create(
            data={"companyId": company_id},
        )
        await self._db.taxesyearendconfig.create(
            data={
                "companyId": company_id,
                "taxDisplay": Json({}),
                "gstRates": Json([]),
                "fedRates": Json([]),
                "adtRates": Json([]),
                "whtRates": Json([]),
                "taxRegions": Json([]),
            },
        )
        for tpl in ROLE_TEMPLATES:
            perms = [str(p) for p in tpl["permissions"]]
            role = await self._db.role.create(
                data={
                    "companyId": company_id,
                    "name": tpl["name"],
                    "code": tpl["code"],
                    "description": tpl.get("description"),
                    "isSystem": bool(tpl.get("isSystem", False)),
                    "isTemplate": True,
                    "sortOrder": int(tpl.get("sortOrder", 0)),
                    "permissions": Json(perms),
                },
            )
            await self._role_permissions.replace_for_role(role_id=role.id, codes=perms)

        # Seed a working chart of accounts + posting defaults so the company can
        # post immediately (see seed_chart_and_defaults — idempotent).
        await self.seed_chart_and_defaults(company_id=company_id)

    async def seed_chart_and_defaults(self, *, company_id: str) -> None:
        """Idempotently ensure a chart of accounts and Smart Settings posting defaults.

        Safe to call on bootstrap AND as a backfill for existing companies: the
        chart is only seeded when the company has none, and a posting default is
        only wired when it is currently unset AND the target nominal actually
        exists on the chart (so a company with a custom chart is never pointed at
        a non-existent code).
        """

        await self._coa.seed_default_chart(company_id=company_id)

        row = await self._smart_settings.get_for_company(company_id=company_id)
        payload: dict = dict(row.payload) if row and isinstance(row.payload, dict) else {}
        defaults: dict = dict(payload.get("defaults") or {})

        wanted_codes = list(set(DEFAULT_POSTING_DEFAULTS.values()))
        present = set(
            (
                await self._coa.nominal_ids_by_codes(
                    company_id=company_id, codes=wanted_codes
                )
            ).keys()
        )

        changed = False
        for key, code in DEFAULT_POSTING_DEFAULTS.items():
            if not defaults.get(key) and code in present:
                defaults[key] = code
                changed = True

        if changed:
            payload["defaults"] = defaults
            await self._smart_settings.upsert_payload(
                company_id=company_id, payload=payload
            )

    async def seed_missing_template_roles(
        self, *, company_id: str
    ) -> list[dict[str, str]]:
        """Create system role templates missing from an existing company."""

        created: list[dict[str, str]] = []
        for tpl in ROLE_TEMPLATES:
            code = str(tpl["code"])
            name = str(tpl["name"])
            existing = await self._db.role.find_first(
                where={
                    "companyId": company_id,
                    "OR": [{"code": code}, {"name": name}],
                },
            )
            if existing is not None:
                if not existing.code:
                    await self._db.role.update(
                        where={"id": existing.id},
                        data={
                            "code": code,
                            "sortOrder": int(tpl.get("sortOrder", 0)),
                            "isSystem": bool(tpl.get("isSystem", False)),
                        },
                    )
                continue

            perms = [str(p) for p in tpl["permissions"]]
            role = await self._db.role.create(
                data={
                    "companyId": company_id,
                    "name": name,
                    "code": code,
                    "description": tpl.get("description"),
                    "isSystem": bool(tpl.get("isSystem", False)),
                    "isTemplate": True,
                    "sortOrder": int(tpl.get("sortOrder", 0)),
                    "permissions": Json(perms),
                },
            )
            await self._role_permissions.replace_for_role(role_id=role.id, codes=perms)
            created.append({"id": role.id, "name": role.name, "code": code})
        return created

    async def assign_admin_role(
        self, *, company_id: str, user_id: str
    ) -> None:
        """Attach the Super Admin role to the founding user's membership."""

        role = await self._db.role.find_first(
            where={"companyId": company_id, "code": "super_admin"},
        )
        if role is None:
            role = await self._db.role.find_first(
                where={"companyId": company_id, "name": "Super Admin"},
            )
        if role is None:
            return
        membership = await self._db.companymembership.find_unique(
            where={"companyId_userId": {"companyId": company_id, "userId": user_id}},
        )
        if membership is None:
            return
        await self._db.companymembership.update(
            where={"id": membership.id},
            data={"roleId": role.id},
        )
        existing = await self._db.membershiprole.find_first(
            where={"membershipId": membership.id, "roleId": role.id},
        )
        if existing is None:
            await self._db.membershiprole.create(
                data={"membershipId": membership.id, "roleId": role.id, "isPrimary": True},
            )
