"""Company module subscription gates — P11."""

from __future__ import annotations

from app.constants.module_codes import ALL_MODULE_CODES, DEFAULT_ENABLED_MODULES
from app.core.exceptions import ForbiddenError
from prisma_generated import Prisma


class ModuleEntitlementService:
    def __init__(self, *, prisma: Prisma) -> None:
        self._db = prisma

    async def list_entitlements(self, *, company_id: str) -> list[dict[str, object]]:
        rows = await self._db.companymoduleentitlement.find_many(
            where={"companyId": company_id},
            order={"moduleCode": "asc"},
        )
        if not rows:
            return [
                {"moduleCode": code, "enabled": True}
                for code in sorted(DEFAULT_ENABLED_MODULES)
            ]
        known = {r.moduleCode: r.enabled for r in rows}
        out: list[dict[str, object]] = []
        for code in sorted(ALL_MODULE_CODES):
            out.append({"moduleCode": code, "enabled": known.get(code, True)})
        return out

    async def replace_entitlements(
        self, *, company_id: str, entitlements: list[dict[str, object]]
    ) -> list[dict[str, object]]:
        await self._db.companymoduleentitlement.delete_many(
            where={"companyId": company_id}
        )
        for row in entitlements:
            code = str(row.get("moduleCode") or "").strip().lower()
            if code not in ALL_MODULE_CODES:
                continue
            await self._db.companymoduleentitlement.create(
                data={
                    "companyId": company_id,
                    "moduleCode": code,
                    "enabled": bool(row.get("enabled", True)),
                }
            )
        return await self.list_entitlements(company_id=company_id)

    async def is_enabled(self, *, company_id: str, module_code: str) -> bool:
        code = module_code.strip().lower()
        row = await self._db.companymoduleentitlement.find_unique(
            where={
                "companyId_moduleCode": {
                    "companyId": company_id,
                    "moduleCode": code,
                }
            }
        )
        if row is None:
            return code in DEFAULT_ENABLED_MODULES
        return row.enabled

    async def assert_enabled(self, *, company_id: str, module_code: str) -> None:
        if not await self.is_enabled(company_id=company_id, module_code=module_code):
            raise ForbiddenError(
                f"Module '{module_code}' is not enabled for this company subscription."
            )
