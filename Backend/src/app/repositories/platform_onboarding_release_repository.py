"""Platform-wide What's New CMS — P52."""

from __future__ import annotations

from typing import Any

from prisma_generated import Prisma
from prisma_generated.errors import TableNotFoundError


class PlatformOnboardingReleaseRepository:
    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_all(self, *, active_only: bool = False) -> list[dict[str, Any]]:
        where: dict[str, Any] = {}
        if active_only:
            where["isActive"] = True
        try:
            rows = await self._db.platformonboardingrelease.find_many(
                where=where,
                order=[{"sortOrder": "asc"}, {"publishedAt": "desc"}],
            )
        except TableNotFoundError:
            return []
        return [self._to_dict(r) for r in rows]

    async def create(
        self,
        *,
        release_key: str,
        version: str,
        title: str,
        summary: str,
        published_at: str,
        tour_id: str | None,
        href: str | None,
        permissions: list[str],
        is_active: bool = True,
        sort_order: int = 0,
    ) -> dict[str, Any]:
        row = await self._db.platformonboardingrelease.create(
            data={
                "releaseKey": release_key,
                "version": version,
                "title": title,
                "summary": summary,
                "publishedAt": published_at,
                "tourId": tour_id,
                "href": href,
                "permissions": permissions,
                "isActive": is_active,
                "sortOrder": sort_order,
            },
        )
        return self._to_dict(row)

    async def update(self, *, item_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        existing = await self._db.platformonboardingrelease.find_unique(where={"id": item_id})
        if existing is None:
            return None
        row = await self._db.platformonboardingrelease.update(where={"id": item_id}, data=data)
        return self._to_dict(row)

    async def delete(self, *, item_id: str) -> bool:
        existing = await self._db.platformonboardingrelease.find_unique(where={"id": item_id})
        if existing is None:
            return False
        await self._db.platformonboardingrelease.delete(where={"id": item_id})
        return True

    @staticmethod
    def _to_dict(row: Any) -> dict[str, Any]:
        perms = row.permissions if isinstance(row.permissions, list) else []
        return {
            "id": row.releaseKey,
            "dbId": row.id,
            "version": row.version,
            "title": row.title,
            "summary": row.summary,
            "publishedAt": row.publishedAt,
            "tourId": row.tourId,
            "href": row.href,
            "permissions": [str(p) for p in perms],
            "isActive": row.isActive,
            "sortOrder": row.sortOrder,
            "source": "platform",
        }
