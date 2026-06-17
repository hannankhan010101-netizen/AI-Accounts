"""Supplier payment (VP) persistence — catalog §6.4."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from prisma_generated import Prisma
from prisma_generated.models import SupplierPayment

from app.services.party_snapshot_service import PartySnapshotService


class SupplierPaymentRepository:
    """Header-only payments; allocation against bills lands in Phase 5.4."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def get_payment(
        self, *, company_id: str, payment_id: str
    ) -> SupplierPayment | None:
        row = await self._db.supplierpayment.find_unique(where={"id": payment_id})
        if row is None or row.companyId != company_id:
            return None
        return row

    async def list_allocations(self, *, payment_id: str) -> list[dict]:
        rows = await self._db.supplierpaymentallocation.find_many(
            where={"supplierPaymentId": payment_id},
        )
        return [
            {
                "id": a.id,
                "supplierBillId": a.supplierBillId,
                "amount": str(a.amount),
            }
            for a in rows
        ]

    async def list_payments(
        self, *, company_id: str, take: int = 50
    ) -> list[SupplierPayment]:
        """Recent supplier payments for AP overview."""

        return await self._db.supplierpayment.find_many(
            where={"companyId": company_id},
            order={"paymentDate": "desc"},
            take=take,
        )

    async def create_payment(
        self,
        *,
        company_id: str,
        voucher_number: str,
        payment_date: datetime,
        supplier_id: str,
        bank_account_id: str,
        total_amount: Decimal,
        journal_id: str | None = None,
        custom_fields: dict | None = None,
        payment_id: str | None = None,
        status: str = "posted",
    ) -> SupplierPayment:
        """Persist payment header with optional GL journal link."""

        data: dict = {
                "companyId": company_id,
                "voucherNumber": voucher_number,
                "paymentDate": payment_date,
                "supplierId": supplier_id,
                "bankAccountId": bank_account_id,
                "totalAmount": total_amount,
                "journalId": journal_id,
                "status": status,
            }
        if payment_id:
            data["id"] = payment_id
        if custom_fields:
            data["customFields"] = custom_fields
        data.update(
            await PartySnapshotService(self._db).supplier_fields(
                company_id=company_id, supplier_id=supplier_id
            )
        )
        return await self._db.supplierpayment.create(data=data)

    async def link_payment_journal(
        self,
        *,
        payment_id: str,
        journal_id: str,
        status: str = "posted",
    ) -> SupplierPayment:
        return await self._db.supplierpayment.update(
            where={"id": payment_id},
            data={"journalId": journal_id, "status": status},
        )

    async def void_payment(self, *, company_id: str, payment_id: str) -> None:
        row = await self.get_payment(company_id=company_id, payment_id=payment_id)
        if row is None:
            raise ValueError("Supplier payment not found")
        await self._db.supplierpaymentallocation.delete_many(
            where={"supplierPaymentId": payment_id},
        )
        await self._db.supplierpayment.update(
            where={"id": payment_id},
            data={"status": "voided"},
        )
