"""Purchase order (PO) persistence — catalog §6.2."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from prisma_generated import Prisma
from prisma_generated.models import PurchaseOrder

from app.services.party_snapshot_service import PartySnapshotService


class PurchaseOrderRepository:
    """Order lifecycle in_progress → approved → billed."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_orders(self, *, company_id: str, take: int = 50) -> list[PurchaseOrder]:
        return await self._db.purchaseorder.find_many(
            where={"companyId": company_id},
            order={"orderDate": "desc"},
            take=take,
            include={"lines": True},
        )

    async def get_order(self, *, company_id: str, order_id: str) -> PurchaseOrder | None:
        row = await self._db.purchaseorder.find_unique(
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
        supplier_id: str,
        lines: list[dict],
    ) -> PurchaseOrder:
        total = sum((Decimal(str(l["lineTotal"])) for l in lines), Decimal(0))
        data = {
                "companyId": company_id,
                "orderNumber": order_number,
                "orderDate": order_date,
                "supplierId": supplier_id,
                "totalAmount": total,
                "lines": {"create": lines},
            }
        data.update(
            await PartySnapshotService(self._db).supplier_fields(
                company_id=company_id, supplier_id=supplier_id
            )
        )
        return await self._db.purchaseorder.create(
            data=data,
            include={"lines": True},
        )

    async def update_status(
        self, *, company_id: str, order_id: str, status: str
    ) -> PurchaseOrder:
        allowed = {"in_progress", "approved", "rejected", "billed"}
        if status not in allowed:
            raise ValueError(f"status must be one of {sorted(allowed)}")
        existing = await self._db.purchaseorder.find_unique(where={"id": order_id})
        if existing is None or existing.companyId != company_id:
            raise ValueError("Purchase order not found for this company")
        return await self._db.purchaseorder.update(
            where={"id": order_id},
            data={"status": status},
            include={"lines": True},
        )
