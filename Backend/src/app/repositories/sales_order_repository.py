"""Sales order (SO) persistence — catalog §5.3."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from prisma_generated import Prisma
from prisma_generated.models import SalesOrder

from app.services.party_snapshot_service import PartySnapshotService


class SalesOrderRepository:
    """Order lifecycle in_progress → approved → invoiced."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_orders(self, *, company_id: str, take: int = 50) -> list[SalesOrder]:
        return await self._db.salesorder.find_many(
            where={"companyId": company_id},
            order={"orderDate": "desc"},
            take=take,
            include={"lines": True},
        )

    async def get_order(self, *, company_id: str, order_id: str) -> SalesOrder | None:
        row = await self._db.salesorder.find_unique(
            where={"id": order_id},
            include={"lines": True},
        )
        if row is None or row.companyId != company_id:
            return None
        return row

    async def create_order(
        self,
        *,
        company_id: str,
        order_number: str,
        order_date: datetime,
        customer_id: str,
        lines: list[dict],
    ) -> SalesOrder:
        total = sum((Decimal(str(l["lineTotal"])) for l in lines), Decimal(0))
        data = {
                "companyId": company_id,
                "orderNumber": order_number,
                "orderDate": order_date,
                "customerId": customer_id,
                "totalAmount": total,
                "lines": {"create": lines},
            }
        data.update(
            await PartySnapshotService(self._db).customer_fields(
                company_id=company_id, customer_id=customer_id
            )
        )
        return await self._db.salesorder.create(
            data=data,
            include={"lines": True},
        )

    async def update_status(
        self, *, company_id: str, order_id: str, status: str
    ) -> SalesOrder:
        allowed = {"in_progress", "approved", "rejected", "invoiced"}
        if status not in allowed:
            raise ValueError(f"status must be one of {sorted(allowed)}")
        existing = await self._db.salesorder.find_unique(where={"id": order_id})
        if existing is None or existing.companyId != company_id:
            raise ValueError("Sales order not found for this company")
        return await self._db.salesorder.update(
            where={"id": order_id},
            data={"status": status},
            include={"lines": True},
        )
