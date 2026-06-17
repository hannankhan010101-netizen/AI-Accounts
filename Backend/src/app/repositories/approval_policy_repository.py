"""Authorisation / approval policy storage."""

from __future__ import annotations

from prisma_generated import Prisma
from prisma_generated.models import ApprovalPolicy


class ApprovalPolicyRepository:
    """Per-entity-type JSON rules for draft/approve flows."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_for_company(self, *, company_id: str) -> list[ApprovalPolicy]:
        """Return all configured policies for a tenant."""

        return await self._db.approvalpolicy.find_many(where={"companyId": company_id})

    async def upsert(
        self,
        *,
        company_id: str,
        entity_type: str,
        rules: dict,
    ) -> ApprovalPolicy:
        """Replace rules for ``entity_type`` or insert when missing."""

        existing = await self._db.approvalpolicy.find_first(
            where={"companyId": company_id, "entityType": entity_type}
        )
        if existing is None:
            return await self._db.approvalpolicy.create(
                data={"companyId": company_id, "entityType": entity_type, "rules": rules}
            )
        return await self._db.approvalpolicy.update(
            where={"id": existing.id},
            data={"rules": rules},
        )
