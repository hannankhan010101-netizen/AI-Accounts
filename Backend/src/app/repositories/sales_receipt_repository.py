"""Customer receipt (SR) persistence — catalog §5.8."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from prisma_generated import Prisma
from prisma_generated.models import SalesReceipt

from app.services.party_snapshot_service import PartySnapshotService


class SalesReceiptRepository:
    """Header-only receipts; allocation lines against invoices land in Phase 4.6."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def get_receipt(
        self, *, company_id: str, receipt_id: str
    ) -> SalesReceipt | None:
        row = await self._db.salesreceipt.find_unique(where={"id": receipt_id})
        if row is None or row.companyId != company_id:
            return None
        return row

    async def list_allocations(self, *, receipt_id: str) -> list[dict]:
        rows = await self._db.salesreceiptallocation.find_many(
            where={"salesReceiptId": receipt_id},
        )
        return [
            {
                "id": a.id,
                "salesInvoiceId": a.salesInvoiceId,
                "amount": str(a.amount),
            }
            for a in rows
        ]

    async def list_receipts(self, *, company_id: str, take: int = 50) -> list[SalesReceipt]:
        return await self._db.salesreceipt.find_many(
            where={"companyId": company_id},
            order={"receiptDate": "desc"},
            take=take,
        )

    async def create_receipt(
        self,
        *,
        company_id: str,
        receipt_number: str,
        receipt_date: datetime,
        customer_id: str,
        bank_account_id: str,
        total_amount: Decimal,
        journal_id: str | None = None,
        custom_fields: dict | None = None,
        receipt_id: str | None = None,
        status: str = "posted",
    ) -> SalesReceipt:
        """Persist receipt header with optional GL journal link."""

        data: dict = {
                "companyId": company_id,
                "receiptNumber": receipt_number,
                "receiptDate": receipt_date,
                "customerId": customer_id,
                "bankAccountId": bank_account_id,
                "totalAmount": total_amount,
                "journalId": journal_id,
                "status": status,
            }
        if receipt_id:
            data["id"] = receipt_id
        if custom_fields:
            data["customFields"] = custom_fields
        data.update(
            await PartySnapshotService(self._db).customer_fields(
                company_id=company_id, customer_id=customer_id
            )
        )
        return await self._db.salesreceipt.create(data=data)

    async def link_receipt_journal(
        self,
        *,
        receipt_id: str,
        journal_id: str,
        status: str = "posted",
    ) -> SalesReceipt:
        return await self._db.salesreceipt.update(
            where={"id": receipt_id},
            data={"journalId": journal_id, "status": status},
        )

    async def void_receipt(self, *, company_id: str, receipt_id: str) -> None:
        row = await self.get_receipt(company_id=company_id, receipt_id=receipt_id)
        if row is None:
            raise ValueError("Sales receipt not found")
        await self._db.salesreceiptallocation.delete_many(
            where={"salesReceiptId": receipt_id},
        )
        await self._db.salesreceipt.update(
            where={"id": receipt_id},
            data={"status": "voided"},
        )
