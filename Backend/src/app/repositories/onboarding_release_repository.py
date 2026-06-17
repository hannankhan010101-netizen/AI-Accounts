"""Tenant What's New release CMS — P51."""

from __future__ import annotations

from typing import Any

from prisma_generated import Prisma
from prisma_generated.errors import TableNotFoundError


class OnboardingReleaseRepository:
    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_for_company(
        self, *, company_id: str, active_only: bool = False
    ) -> list[dict[str, Any]]:
        where: dict[str, Any] = {"companyId": company_id}
        if active_only:
            where["isActive"] = True
        try:
            rows = await self._db.onboardingreleaseitem.find_many(
                where=where,
                order=[{"sortOrder": "asc"}, {"publishedAt": "desc"}],
            )
        except TableNotFoundError:
            return []
        return [self._to_dict(r) for r in rows]

    async def get(self, *, company_id: str, item_id: str) -> dict[str, Any] | None:
        row = await self._db.onboardingreleaseitem.find_first(
            where={"id": item_id, "companyId": company_id},
        )
        return self._to_dict(row) if row else None

    async def create(
        self,
        *,
        company_id: str,
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
        row = await self._db.onboardingreleaseitem.create(
            data={
                "companyId": company_id,
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

    async def update(
        self,
        *,
        company_id: str,
        item_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any] | None:
        existing = await self._db.onboardingreleaseitem.find_first(
            where={"id": item_id, "companyId": company_id},
        )
        if existing is None:
            return None
        row = await self._db.onboardingreleaseitem.update(
            where={"id": item_id},
            data=data,
        )
        return self._to_dict(row)

    async def delete(self, *, company_id: str, item_id: str) -> bool:
        existing = await self._db.onboardingreleaseitem.find_first(
            where={"id": item_id, "companyId": company_id},
        )
        if existing is None:
            return False
        await self._db.onboardingreleaseitem.delete(where={"id": item_id})
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
            "source": "tenant",
        }
