"""Sales invoice (SI) persistence — catalog §5.4."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from prisma_generated import Prisma
from prisma_generated.models import SalesInvoice

from app.services.party_snapshot_service import PartySnapshotService


class SalesInvoiceRepository:
    """Invoice header + lines. GL posting hook lands in a Phase 4.4 follow-up."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_invoices(self, *, company_id: str, take: int = 50) -> list[SalesInvoice]:
        """Return recent invoice headers (lines loaded on detail only)."""

        return await self._db.salesinvoice.find_many(
            where={"companyId": company_id},
            order={"invoiceDate": "desc"},
            take=take,
        )

    async def get_invoice(
        self,
        *,
        company_id: str,
        invoice_id: str,
    ) -> SalesInvoice | None:
        """Single invoice with lines for the detail screen."""

        row = await self._db.salesinvoice.find_unique(
            where={"id": invoice_id},
            include={"lines": True},
        )
        if row is None or row.companyId != company_id:
            return None
        return row

    async def create_invoice(
        self,
        *,
        company_id: str,
        invoice_number: str,
        invoice_date: datetime,
        customer_id: str,
        lines: list[dict],
        journal_id: str | None = None,
        custom_fields: dict | None = None,
    ) -> SalesInvoice:
        """
        Insert invoice header + lines. ``lines`` items expect
        ``{productCode, quantity, rate, lineTotal, projectCode}``;
        ``lineTotal`` is computed by the caller before this call. ``journal_id``
        links the GL posting that the posting service wrote.
        """

        total = sum((Decimal(str(l["lineTotal"])) for l in lines), Decimal(0))
        posted = journal_id is not None
        data: dict = {
                "companyId": company_id,
                "invoiceNumber": invoice_number,
                "invoiceDate": invoice_date,
                "customerId": customer_id,
                "totalAmount": total,
                "remainingAmount": total if posted else Decimal(0),
                "status": "posted" if posted else "draft",
                "journalId": journal_id,
                "lines": {"create": lines},
            }
        if custom_fields:
            data["customFields"] = custom_fields
        data.update(
            await PartySnapshotService(self._db).customer_fields(
                company_id=company_id, customer_id=customer_id
            )
        )
        return await self._db.salesinvoice.create(
            data=data,
            include={"lines": True},
        )

    async def mark_posted(
        self,
        *,
        company_id: str,
        invoice_id: str,
        journal_id: str,
    ) -> SalesInvoice:
        """Transition draft invoice to posted after GL approval."""

        row = await self.get_invoice(company_id=company_id, invoice_id=invoice_id)
        if row is None:
            raise ValueError("Sales invoice not found")
        return await self._db.salesinvoice.update(
            where={"id": invoice_id},
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
        invoice_id: str,
        invoice_date: datetime,
        customer_id: str,
        lines: list[dict],
    ) -> SalesInvoice:
        """Replace header and lines on a draft invoice (not posted to GL)."""

        row = await self.get_invoice(company_id=company_id, invoice_id=invoice_id)
        if row is None:
            raise ValueError("Sales invoice not found")
        if row.status != "draft" or row.journalId is not None:
            raise ValueError("Only draft invoices can be edited")
        total = sum((Decimal(str(l["lineTotal"])) for l in lines), Decimal(0))
        update_data: dict = {
                "invoiceDate": invoice_date,
                "customerId": customer_id,
                "totalAmount": total,
                "lines": {"deleteMany": {}, "create": lines},
            }
        update_data.update(
            await PartySnapshotService(self._db).customer_fields(
                company_id=company_id, customer_id=customer_id
            )
        )
        return await self._db.salesinvoice.update(
            where={"id": invoice_id},
            data=update_data,
            include={"lines": True},
        )

    async def update_status(
        self,
        *,
        company_id: str,
        invoice_id: str,
        status: str,
    ) -> SalesInvoice:
        row = await self.get_invoice(company_id=company_id, invoice_id=invoice_id)
        if row is None:
            raise ValueError("Sales invoice not found")
        return await self._db.salesinvoice.update(
            where={"id": invoice_id},
            data={"status": status},
            include={"lines": True},
        )
