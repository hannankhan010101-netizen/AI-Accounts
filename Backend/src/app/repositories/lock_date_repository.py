"""Lock date policy."""

from __future__ import annotations

from datetime import datetime

from prisma_generated import Prisma
from prisma_generated.models import LockDateSettings


class LockDateRepository:
    """Global lock date per company."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def get_for_company(self, *, company_id: str) -> LockDateSettings | None:
        """Return lock settings row."""

        return await self._db.lockdatesettings.find_unique(where={"companyId": company_id})

    async def upsert_global(self, *, company_id: str, global_lock_date: datetime | None) -> LockDateSettings:
        """Set global lock date."""

        return await self._db.lockdatesettings.upsert(
            where={"companyId": company_id},
            data={
                "create": {"companyId": company_id, "globalLockDate": global_lock_date},
                "update": {"globalLockDate": global_lock_date},
            },
        )

    async def get_user_extension(
        self, *, company_id: str, user_id: str
    ) -> datetime | None:
        """Return per-user extended lock date when configured (P4)."""

        settings = await self.get_for_company(company_id=company_id)
        if settings is None:
            return None
        row = await self._db.lockdateperuser.find_unique(
            where={
                "lockDateSettingsId_userId": {
                    "lockDateSettingsId": settings.id,
                    "userId": user_id,
                }
            }
        )
        return row.extendedLockDate if row else None

    async def upsert_user_extension(
        self,
        *,
        company_id: str,
        user_id: str,
        extended_lock_date: datetime,
    ) -> None:
        settings = await self._db.lockdatesettings.upsert(
            where={"companyId": company_id},
            data={
                "create": {"companyId": company_id},
                "update": {},
            },
        )
        await self._db.lockdateperuser.upsert(
            where={
                "lockDateSettingsId_userId": {
                    "lockDateSettingsId": settings.id,
                    "userId": user_id,
                }
            },
            data={
                "create": {
                    "lockDateSettingsId": settings.id,
                    "userId": user_id,
                    "extendedLockDate": extended_lock_date,
                },
                "update": {"extendedLockDate": extended_lock_date},
            },
        )

    async def list_user_extensions(
        self, *, company_id: str
    ) -> list[dict[str, str | None]]:
        settings = await self.get_for_company(company_id=company_id)
        if settings is None:
            return []
        rows = await self._db.lockdateperuser.find_many(
            where={"lockDateSettingsId": settings.id},
        )
        return [
            {
                "userId": row.userId,
                "extendedLockDate": row.extendedLockDate.isoformat()
                if row.extendedLockDate
                else None,
            }
            for row in rows
        ]
