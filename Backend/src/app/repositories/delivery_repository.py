"""Delivery Note (GDNSI/GDNSO) and Goods Receipt Note (GRNPO/GRNVI) persistence — Sprint 12."""

from __future__ import annotations

from datetime import datetime

from prisma_generated import Prisma
from prisma_generated.models import DeliveryNote, GoodsReceiptNote

from app.services.party_snapshot_service import PartySnapshotService


class DeliveryNoteRepository:
    """§5.6 — delivery against an invoice (GDNSI) or sales order (GDNSO)."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_notes(self, *, company_id: str, take: int = 50) -> list[DeliveryNote]:
        return await self._db.deliverynote.find_many(
            where={"companyId": company_id},
            order={"deliveryDate": "desc"},
            take=take,
            include={"lines": True},
        )

    async def get_note(
        self, *, company_id: str, note_id: str
    ) -> DeliveryNote | None:
        row = await self._db.deliverynote.find_unique(
            where={"id": note_id},
            include={"lines": True},
        )
        if row is None or row.companyId != company_id:
            return None
        return row

    async def create_note(
        self,
        *,
        company_id: str,
        voucher_number: str,
        delivery_date: datetime,
        customer_id: str,
        source_kind: str,
        source_id: str | None,
        notes: str | None,
        lines: list[dict],
    ) -> DeliveryNote:
        if source_kind not in {"GDNSI", "GDNSO", "manual"}:
            raise ValueError("sourceKind must be GDNSI / GDNSO / manual")
        data = {
                "companyId": company_id,
                "voucherNumber": voucher_number,
                "deliveryDate": delivery_date,
                "customerId": customer_id,
                "sourceKind": source_kind,
                "sourceId": source_id,
                "notes": notes,
                "status": "delivered",
                "lines": {"create": lines},
            }
        data.update(
            await PartySnapshotService(self._db).customer_fields(
                company_id=company_id, customer_id=customer_id
            )
        )
        return await self._db.deliverynote.create(
            data=data,
            include={"lines": True},
        )

    async def list_by_source(
        self,
        *,
        company_id: str,
        source_kind: str,
        source_id: str,
    ) -> list[DeliveryNote]:
        return await self._db.deliverynote.find_many(
            where={
                "companyId": company_id,
                "sourceKind": source_kind,
                "sourceId": source_id,
            },
            include={"lines": True},
        )

    async def update_status(
        self,
        *,
        company_id: str,
        note_id: str,
        status: str,
    ) -> DeliveryNote:
        row = await self.get_note(company_id=company_id, note_id=note_id)
        if row is None:
            raise ValueError("Delivery note not found")
        return await self._db.deliverynote.update(
            where={"id": note_id},
            data={"status": status},
            include={"lines": True},
        )


class GoodsReceiptNoteRepository:
    """§6 — goods receipt against a PO (GRNPO) or bill (GRNVI)."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_notes(
        self, *, company_id: str, take: int = 50
    ) -> list[GoodsReceiptNote]:
        return await self._db.goodsreceiptnote.find_many(
            where={"companyId": company_id},
            order={"receiptDate": "desc"},
            take=take,
            include={"lines": True},
        )

    async def get_note(
        self, *, company_id: str, note_id: str
    ) -> GoodsReceiptNote | None:
        row = await self._db.goodsreceiptnote.find_unique(
            where={"id": note_id},
            include={"lines": True},
        )
        if row is None or row.companyId != company_id:
            return None
        return row

    async def create_note(
        self,
        *,
        company_id: str,
        voucher_number: str,
        receipt_date: datetime,
        supplier_id: str,
        source_kind: str,
        source_id: str | None,
        notes: str | None,
        lines: list[dict],
    ) -> GoodsReceiptNote:
        if source_kind not in {"GRNPO", "GRNVI", "manual"}:
            raise ValueError("sourceKind must be GRNPO / GRNVI / manual")
        data = {
                "companyId": company_id,
                "voucherNumber": voucher_number,
                "receiptDate": receipt_date,
                "supplierId": supplier_id,
                "sourceKind": source_kind,
                "sourceId": source_id,
                "notes": notes,
                "status": "received",
                "lines": {"create": lines},
            }
        data.update(
            await PartySnapshotService(self._db).supplier_fields(
                company_id=company_id, supplier_id=supplier_id
            )
        )
        return await self._db.goodsreceiptnote.create(
            data=data,
            include={"lines": True},
        )

    async def list_by_source(
        self,
        *,
        company_id: str,
        source_kind: str,
        source_id: str,
    ) -> list[GoodsReceiptNote]:
        return await self._db.goodsreceiptnote.find_many(
            where={
                "companyId": company_id,
                "sourceKind": source_kind,
                "sourceId": source_id,
            },
            include={"lines": True},
        )

    async def update_status(
        self,
        *,
        company_id: str,
        note_id: str,
        status: str,
    ) -> GoodsReceiptNote:
        row = await self.get_note(company_id=company_id, note_id=note_id)
        if row is None:
            raise ValueError("Goods receipt note not found")
        return await self._db.goodsreceiptnote.update(
            where={"id": note_id},
            data={"status": status},
            include={"lines": True},
        )
