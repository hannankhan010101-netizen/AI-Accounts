"""Sales credit (SC) persistence — catalog §5.5."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from prisma_generated import Prisma
from prisma_generated.models import SalesCredit

from app.services.party_snapshot_service import PartySnapshotService


class SalesCreditRepository:
    """Credit note reversing AR. GL impact: DR sales / CR receivables."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_credits(self, *, company_id: str, take: int = 50) -> list[SalesCredit]:
        return await self._db.salescredit.find_many(
            where={"companyId": company_id},
            order={"creditDate": "desc"},
            take=take,
            include={"lines": True},
        )

    async def get_credit(self, *, company_id: str, credit_id: str) -> SalesCredit | None:
        row = await self._db.salescredit.find_unique(
            where={"id": credit_id},
            include={"lines": True},
        )
        if row is None or row.companyId != company_id:
            return None
        return row

    async def create_credit(
        self,
        *,
        company_id: str,
        credit_number: str,
        credit_date: datetime,
        customer_id: str,
        lines: list[dict],
        journal_id: str | None = None,
        credit_id: str | None = None,
    ) -> SalesCredit:
        total = sum((Decimal(str(l["lineTotal"])) for l in lines), Decimal(0))
        data: dict[str, Any] = {
                "companyId": company_id,
                "creditNumber": credit_number,
                "creditDate": credit_date,
                "customerId": customer_id,
                "totalAmount": total,
                "status": "posted",
                "journalId": journal_id,
                "lines": {"create": lines},
            }
        if credit_id:
            data["id"] = credit_id
        data.update(
            await PartySnapshotService(self._db).customer_fields(
                company_id=company_id, customer_id=customer_id
            )
        )
        return await self._db.salescredit.create(
            data=data,
            include={"lines": True},
        )

    async def update_status(
        self,
        *,
        company_id: str,
        credit_id: str,
        status: str,
    ) -> SalesCredit:
        row = await self.get_credit(company_id=company_id, credit_id=credit_id)
        if row is None:
            raise ValueError("Sales credit not found")
        return await self._db.salescredit.update(
            where={"id": credit_id},
            data={"status": status},
            include={"lines": True},
        )
