"""Write-time party code/name snapshots on document headers (Step 3)."""

from __future__ import annotations

from prisma_generated import Prisma

from app.core.exceptions import ValidationAppError


class PartySnapshotService:
    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def customer_snapshot(
        self, *, company_id: str, customer_id: str
    ) -> tuple[str, str]:
        row = await self._db.customer.find_unique(where={"id": customer_id})
        if row is None or row.companyId != company_id:
            raise ValidationAppError("Customer not found for this company")
        return row.code, row.name

    async def supplier_snapshot(
        self, *, company_id: str, supplier_id: str
    ) -> tuple[str, str]:
        row = await self._db.supplier.find_unique(where={"id": supplier_id})
        if row is None or row.companyId != company_id:
            raise ValidationAppError("Supplier not found for this company")
        return row.code, row.name

    async def customer_fields(
        self, *, company_id: str, customer_id: str
    ) -> dict[str, str]:
        code, name = await self.customer_snapshot(
            company_id=company_id, customer_id=customer_id
        )
        return {"customerCode": code, "customerName": name}

    async def supplier_fields(
        self, *, company_id: str, supplier_id: str
    ) -> dict[str, str]:
        code, name = await self.supplier_snapshot(
            company_id=company_id, supplier_id=supplier_id
        )
        return {"supplierCode": code, "supplierName": name}
