"""Approval request queue persistence — P3."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from prisma_generated import Prisma
from prisma_generated.models import ApprovalRequest


class ApprovalRequestRepository:
    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_for_company(
        self, *, company_id: str, status: str | None = None, take: int = 100
    ) -> list[ApprovalRequest]:
        where: dict = {"companyId": company_id}
        if status:
            where["status"] = status
        return await self._db.approvalrequest.find_many(
            where=where,
            order={"createdAt": "desc"},
            take=take,
        )

    async def get_by_id(
        self, *, company_id: str, request_id: str
    ) -> ApprovalRequest | None:
        row = await self._db.approvalrequest.find_unique(where={"id": request_id})
        if row is None or row.companyId != company_id:
            return None
        return row

    async def find_approved_for_entity(
        self, *, company_id: str, entity_type: str, entity_id: str
    ) -> ApprovalRequest | None:
        return await self._db.approvalrequest.find_first(
            where={
                "companyId": company_id,
                "entityType": entity_type,
                "entityId": entity_id,
                "status": "approved",
            },
            order={"approvedAt": "desc"},
        )

    async def create_pending(
        self,
        *,
        company_id: str,
        entity_type: str,
        entity_id: str,
        amount: Decimal,
        requested_by_id: str | None,
        notes: str | None = None,
    ) -> ApprovalRequest:
        return await self._db.approvalrequest.create(
            data={
                "companyId": company_id,
                "entityType": entity_type,
                "entityId": entity_id,
                "amount": amount,
                "status": "pending",
                "requestedById": requested_by_id,
                "notes": notes,
            }
        )

    async def mark_approved(
        self,
        *,
        request_id: str,
        approved_by_id: str | None,
        approved_at: datetime,
    ) -> ApprovalRequest:
        return await self._db.approvalrequest.update(
            where={"id": request_id},
            data={
                "status": "approved",
                "approvedById": approved_by_id,
                "approvedAt": approved_at,
            },
        )

    async def mark_rejected(self, *, request_id: str) -> ApprovalRequest:
        return await self._db.approvalrequest.update(
            where={"id": request_id},
            data={"status": "rejected"},
        )
