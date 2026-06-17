"""Project master data — FA §2.6 / Smart Settings."""

from __future__ import annotations

from prisma_generated import Prisma
from prisma_generated.models import Project


class ProjectRepository:
    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_projects(self, *, company_id: str) -> list[Project]:
        return await self._db.project.find_many(
            where={"companyId": company_id},
            order={"code": "asc"},
        )

    async def create_project(self, *, company_id: str, code: str, name: str) -> Project:
        return await self._db.project.create(
            data={"companyId": company_id, "code": code, "name": name},
        )

    async def update_project(
        self, *, company_id: str, project_id: str, name: str | None, is_active: bool | None
    ) -> Project | None:
        existing = await self._db.project.find_first(
            where={"id": project_id, "companyId": company_id},
        )
        if existing is None:
            return None
        data: dict = {}
        if name is not None:
            data["name"] = name
        if is_active is not None:
            data["isActive"] = is_active
        if not data:
            return existing
        return await self._db.project.update(where={"id": project_id}, data=data)
