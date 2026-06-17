"""Saved transaction templates — FA §3.3."""

from __future__ import annotations

from typing import Any

from prisma_generated import Prisma
from prisma_generated.models import TransactionTemplate


class TransactionTemplateRepository:
    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_for_module(
        self, *, company_id: str, module: str, take: int = 100
    ) -> list[TransactionTemplate]:
        return await self._db.transactiontemplate.find_many(
            where={"companyId": company_id, "module": module},
            order={"name": "asc"},
            take=take,
        )

    async def get_by_id(
        self, *, company_id: str, template_id: str
    ) -> TransactionTemplate | None:
        row = await self._db.transactiontemplate.find_unique(where={"id": template_id})
        if row is None or row.companyId != company_id:
            return None
        return row

    async def create(
        self,
        *,
        company_id: str,
        module: str,
        name: str,
        payload: dict[str, Any],
        created_by: str | None = None,
    ) -> TransactionTemplate:
        return await self._db.transactiontemplate.create(
            data={
                "companyId": company_id,
                "module": module,
                "name": name,
                "payload": payload,
                "createdBy": created_by,
            }
        )

    async def delete(self, *, company_id: str, template_id: str) -> None:
        row = await self.get_by_id(company_id=company_id, template_id=template_id)
        if row is None:
            raise ValueError("Template not found")
        await self._db.transactiontemplate.delete(where={"id": template_id})
