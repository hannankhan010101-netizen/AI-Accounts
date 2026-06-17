"""Quotation (SQ) persistence — catalog §5.2."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from prisma_generated import Prisma
from prisma_generated.models import Quotation

from app.services.party_snapshot_service import PartySnapshotService


class QuotationRepository:
    """Pre-sale quote with line grid; no GL impact."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_quotations(self, *, company_id: str, take: int = 50) -> list[Quotation]:
        return await self._db.quotation.find_many(
            where={"companyId": company_id},
            order={"quotationDate": "desc"},
            take=take,
            include={"lines": True},
        )

    async def get_quotation(self, *, company_id: str, quotation_id: str) -> Quotation | None:
        row = await self._db.quotation.find_unique(
            where={"id": quotation_id},
            include={"lines": True},
        )
        if row is None or row.companyId != company_id:
            return None
        return row

    async def create_quotation(
        self,
        *,
        company_id: str,
        quotation_number: str,
        quotation_date: datetime,
        customer_id: str,
        lines: list[dict],
    ) -> Quotation:
        total = sum((Decimal(str(l["lineTotal"])) for l in lines), Decimal(0))
        data = {
                "companyId": company_id,
                "quotationNumber": quotation_number,
                "quotationDate": quotation_date,
                "customerId": customer_id,
                "totalAmount": total,
                "lines": {"create": lines},
            }
        data.update(
            await PartySnapshotService(self._db).customer_fields(
                company_id=company_id, customer_id=customer_id
            )
        )
        return await self._db.quotation.create(
            data=data,
            include={"lines": True},
        )

    async def update_status(
        self, *, company_id: str, quotation_id: str, status: str
    ) -> Quotation:
        allowed = {"draft", "approved", "rejected", "accepted", "converted"}
        if status not in allowed:
            raise ValueError(f"status must be one of {sorted(allowed)}")
        existing = await self._db.quotation.find_unique(where={"id": quotation_id})
        if existing is None or existing.companyId != company_id:
            raise ValueError("Quotation not found for this company")
        return await self._db.quotation.update(
            where={"id": quotation_id},
            data={"status": status},
            include={"lines": True},
        )
