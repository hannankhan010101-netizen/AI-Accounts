"""User and transaction audit trail."""

from __future__ import annotations

from datetime import datetime

from prisma_generated import Prisma
from prisma_generated.models import AuditLogEntry

from app.core.prisma_data import omit_none


class AuditLogRepository:
    """Append-only audit rows for compliance screens (User Log)."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_filtered(
        self,
        *,
        company_id: str,
        user_id: str | None,
        date_from: datetime | None,
        date_to: datetime | None,
        transaction_types: list[str] | None = None,
        transaction_type_contains: str | None = None,
        transaction_id: str | None = None,
        take: int = 100,
    ) -> list[AuditLogEntry]:
        """Return audit rows with optional actor, date window, and type filter."""

        where: dict = {"companyId": company_id}
        if user_id:
            where["userId"] = user_id
        if transaction_id:
            where["transactionId"] = transaction_id
        if transaction_types:
            if len(transaction_types) == 1:
                where["transactionType"] = transaction_types[0]
            else:
                where["transactionType"] = {"in": transaction_types}
        elif transaction_type_contains:
            where["transactionType"] = {"contains": transaction_type_contains}
        if date_from or date_to:
            where["createdAt"] = {}
            if date_from:
                where["createdAt"]["gte"] = date_from
            if date_to:
                where["createdAt"]["lte"] = date_to
        return await self._db.auditlogentry.find_many(
            where=where,
            order={"createdAt": "desc"},
            take=take,
        )

    async def append(
        self,
        *,
        company_id: str,
        user_id: str | None,
        transaction_type: str,
        transaction_id: str | None,
        status: str | None,
        details: str | None,
    ) -> AuditLogEntry:
        """Record one auditable event."""

        return await self._db.auditlogentry.create(
            data=omit_none(
                {
                    "companyId": company_id,
                    "userId": user_id,
                    "transactionType": transaction_type,
                    "transactionId": transaction_id,
                    "status": status,
                    "details": details,
                }
            )
        )
