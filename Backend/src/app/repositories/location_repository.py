"""Location master data — FA §12.7."""

from __future__ import annotations

from prisma_generated import Prisma
from prisma_generated.models import Location


class LocationRepository:
    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_locations(self, *, company_id: str) -> list[Location]:
        return await self._db.location.find_many(
            where={"companyId": company_id},
            order={"code": "asc"},
        )

    async def create_location(
        self, *, company_id: str, code: str, name: str, is_main: bool = False
    ) -> Location:
        if is_main:
            await self._db.location.update_many(
                where={"companyId": company_id, "isMain": True},
                data={"isMain": False},
            )
        return await self._db.location.create(
            data={
                "companyId": company_id,
                "code": code,
                "name": name,
                "isMain": is_main,
            },
        )

    async def update_location(
        self,
        *,
        company_id: str,
        location_id: str,
        name: str | None,
        is_main: bool | None,
    ) -> Location | None:
        existing = await self._db.location.find_first(
            where={"id": location_id, "companyId": company_id},
        )
        if existing is None:
            return None
        if is_main:
            await self._db.location.update_many(
                where={"companyId": company_id, "isMain": True},
                data={"isMain": False},
            )
        data: dict = {}
        if name is not None:
            data["name"] = name
        if is_main is not None:
            data["isMain"] = is_main
        if not data:
            return existing
        return await self._db.location.update(where={"id": location_id}, data=data)
