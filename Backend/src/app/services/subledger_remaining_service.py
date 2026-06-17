"""Maintain denormalized ``remaining_amount`` on AR/AP documents (Phase 3)."""

from __future__ import annotations

from decimal import Decimal

from prisma_generated import Prisma


class SubledgerRemainingService:
    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def sync_sales_invoice(self, *, invoice_id: str) -> None:
        inv = await self._db.salesinvoice.find_unique(
            where={"id": invoice_id},
            include={"allocations": True},
        )
        if inv is None:
            return
        allocated = sum((a.amount for a in (inv.allocations or [])), Decimal(0))
        remaining = max(Decimal(0), inv.totalAmount - allocated)
        await self._db.salesinvoice.update(
            where={"id": invoice_id},
            data={"remainingAmount": remaining},
        )

    async def sync_supplier_bill(self, *, bill_id: str) -> None:
        bill = await self._db.supplierbill.find_unique(
            where={"id": bill_id},
            include={"allocations": True},
        )
        if bill is None:
            return
        allocated = sum((a.amount for a in (bill.allocations or [])), Decimal(0))
        remaining = max(Decimal(0), bill.totalAmount - allocated)
        await self._db.supplierbill.update(
            where={"id": bill_id},
            data={"remainingAmount": remaining},
        )

    async def sync_sales_invoices(self, *, invoice_ids: list[str]) -> None:
        for invoice_id in dict.fromkeys(invoice_ids):
            await self.sync_sales_invoice(invoice_id=invoice_id)

    async def sync_supplier_bills(self, *, bill_ids: list[str]) -> None:
        for bill_id in dict.fromkeys(bill_ids):
            await self.sync_supplier_bill(bill_id=bill_id)

    async def set_invoice_remaining_on_create(
        self, *, invoice_id: str, total_amount: Decimal
    ) -> None:
        await self._db.salesinvoice.update(
            where={"id": invoice_id},
            data={"remainingAmount": total_amount},
        )

    async def set_bill_remaining_on_create(
        self, *, bill_id: str, total_amount: Decimal
    ) -> None:
        await self._db.supplierbill.update(
            where={"id": bill_id},
            data={"remainingAmount": total_amount},
        )
