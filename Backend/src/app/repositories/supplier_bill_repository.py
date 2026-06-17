"""Supplier bill (VI) persistence — catalog §6.3."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from prisma_generated import Prisma
from prisma_generated.models import SupplierBill

from app.services.party_snapshot_service import PartySnapshotService


class SupplierBillRepository:
    """Purchase invoice header + lines. AP posting hook is Phase 5.3 follow-up."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_bills(self, *, company_id: str, take: int = 50) -> list[SupplierBill]:
        """Return recent bills with lines."""

        return await self._db.supplierbill.find_many(
            where={"companyId": company_id},
            order={"billDate": "desc"},
            take=take,
            include={"lines": True},
        )

    async def get_bill(
        self,
        *,
        company_id: str,
        bill_id: str,
    ) -> SupplierBill | None:
        """Single bill with lines."""

        row = await self._db.supplierbill.find_unique(
            where={"id": bill_id},
            include={"lines": True},
        )
        if row is None or row.companyId != company_id:
            return None
        return row

    async def create_bill(
        self,
        *,
        company_id: str,
        bill_number: str,
        bill_date: datetime,
        supplier_id: str,
        lines: list[dict],
        journal_id: str | None = None,
        custom_fields: dict | None = None,
    ) -> SupplierBill:
        """Insert header + lines. ``lines`` items expect productCode/quantity/rate/lineTotal."""

        total = sum((Decimal(str(l["lineTotal"])) for l in lines), Decimal(0))
        posted = journal_id is not None
        data: dict = {
                "companyId": company_id,
                "billNumber": bill_number,
                "billDate": bill_date,
                "supplierId": supplier_id,
                "totalAmount": total,
                "remainingAmount": total if posted else Decimal(0),
                "status": "posted" if posted else "draft",
                "journalId": journal_id,
                "lines": {"create": lines},
            }
        if custom_fields:
            data["customFields"] = custom_fields
        data.update(
            await PartySnapshotService(self._db).supplier_fields(
                company_id=company_id, supplier_id=supplier_id
            )
        )
        return await self._db.supplierbill.create(
            data=data,
            include={"lines": True},
        )

    async def mark_posted(
        self,
        *,
        company_id: str,
        bill_id: str,
        journal_id: str,
    ) -> SupplierBill:
        row = await self.get_bill(company_id=company_id, bill_id=bill_id)
        if row is None:
            raise ValueError("Supplier bill not found")
        return await self._db.supplierbill.update(
            where={"id": bill_id},
            data={
                "status": "posted",
                "journalId": journal_id,
                "remainingAmount": row.totalAmount,
            },
            include={"lines": True},
        )

    async def update_draft(
        self,
        *,
        company_id: str,
        bill_id: str,
        bill_date: datetime,
        supplier_id: str,
        lines: list[dict],
    ) -> SupplierBill:
        """Replace header and lines on a draft supplier bill."""

        row = await self.get_bill(company_id=company_id, bill_id=bill_id)
        if row is None:
            raise ValueError("Supplier bill not found")
        if row.status != "draft" or row.journalId is not None:
            raise ValueError("Only draft bills can be edited")
        total = sum((Decimal(str(l["lineTotal"])) for l in lines), Decimal(0))
        update_data: dict = {
                "billDate": bill_date,
                "supplierId": supplier_id,
                "totalAmount": total,
                "lines": {"deleteMany": {}, "create": lines},
            }
        update_data.update(
            await PartySnapshotService(self._db).supplier_fields(
                company_id=company_id, supplier_id=supplier_id
            )
        )
        return await self._db.supplierbill.update(
            where={"id": bill_id},
            data=update_data,
            include={"lines": True},
        )

    async def update_status(
        self,
        *,
        company_id: str,
        bill_id: str,
        status: str,
    ) -> SupplierBill:
        row = await self.get_bill(company_id=company_id, bill_id=bill_id)
        if row is None:
            raise ValueError("Supplier bill not found")
        return await self._db.supplierbill.update(
            where={"id": bill_id},
            data={"status": status},
            include={"lines": True},
        )
