"""My Tasks — draft documents and items needing attention (FA header chrome)."""

from __future__ import annotations

import asyncio
from typing import Any

from prisma_generated import Prisma


class MyTasksService:
    def __init__(self, prisma: Prisma) -> None:
        self._db = prisma

    async def list_tasks(self, *, company_id: str) -> list[dict[str, Any]]:
        (
            invoices,
            bills,
            sales_credits,
            supplier_credits,
            quotations,
            sales_orders,
            purchase_orders,
            journals,
        ) = await asyncio.gather(
            self._db.salesinvoice.find_many(
                where={"companyId": company_id, "status": "draft"},
                order={"invoiceDate": "desc"},
                take=50,
            ),
            self._db.supplierbill.find_many(
                where={"companyId": company_id, "status": "draft"},
                order={"billDate": "desc"},
                take=50,
            ),
            self._db.salescredit.find_many(
                where={"companyId": company_id, "status": "draft"},
                order={"creditDate": "desc"},
                take=50,
            ),
            self._db.suppliercredit.find_many(
                where={"companyId": company_id, "status": "draft"},
                order={"creditDate": "desc"},
                take=50,
            ),
            self._db.quotation.find_many(
                where={"companyId": company_id, "status": "draft"},
                order={"quotationDate": "desc"},
                take=50,
            ),
            self._db.salesorder.find_many(
                where={"companyId": company_id, "status": "draft"},
                order={"orderDate": "desc"},
                take=50,
            ),
            self._db.purchaseorder.find_many(
                where={"companyId": company_id, "status": "draft"},
                order={"orderDate": "desc"},
                take=50,
            ),
            self._db.journal.find_many(
                where={"companyId": company_id, "status": "draft"},
                order={"journalDate": "desc"},
                take=50,
            ),
        )

        rows: list[dict[str, Any]] = []

        def add(
            *,
            entity_type: str,
            entity_id: str,
            doc_type: str,
            document_number: str | None,
            document_date,
            summary: str,
        ) -> None:
            rows.append(
                {
                    "entityType": entity_type,
                    "entityId": entity_id,
                    "docType": doc_type,
                    "documentNumber": document_number,
                    "documentDate": document_date.isoformat() if document_date else None,
                    "summary": summary,
                }
            )

        for inv in invoices:
            add(
                entity_type="sales_invoice",
                entity_id=inv.id,
                doc_type="Sale Invoice",
                document_number=inv.invoiceNumber,
                document_date=inv.invoiceDate,
                summary="Draft sale invoice — post or edit",
            )
        for bill in bills:
            add(
                entity_type="supplier_bill",
                entity_id=bill.id,
                doc_type="Supplier Bill",
                document_number=bill.billNumber,
                document_date=bill.billDate,
                summary="Draft supplier bill — post or edit",
            )
        for cr in sales_credits:
            add(
                entity_type="sales_credit",
                entity_id=cr.id,
                doc_type="Sales Credit",
                document_number=cr.creditNumber,
                document_date=cr.creditDate,
                summary="Draft sales credit — post or edit",
            )
        for cr in supplier_credits:
            add(
                entity_type="supplier_credit",
                entity_id=cr.id,
                doc_type="Supplier Credit",
                document_number=cr.creditNumber,
                document_date=cr.creditDate,
                summary="Draft supplier credit — post or edit",
            )
        for q in quotations:
            add(
                entity_type="quotation",
                entity_id=q.id,
                doc_type="Quotation",
                document_number=q.quotationNumber,
                document_date=q.quotationDate,
                summary="Draft quotation — finalize or convert",
            )
        for so in sales_orders:
            add(
                entity_type="sales_order",
                entity_id=so.id,
                doc_type="Sales Order",
                document_number=so.orderNumber,
                document_date=so.orderDate,
                summary="Draft sales order — confirm or convert",
            )
        for po in purchase_orders:
            add(
                entity_type="purchase_order",
                entity_id=po.id,
                doc_type="Purchase Order",
                document_number=po.orderNumber,
                document_date=po.orderDate,
                summary="Draft purchase order — confirm or receive",
            )
        for j in journals:
            add(
                entity_type="journal",
                entity_id=j.id,
                doc_type="Journal",
                document_number=j.journalNumber,
                document_date=j.journalDate,
                summary="Draft journal — post or edit",
            )

        rows.sort(key=lambda r: r.get("documentDate") or "", reverse=True)
        return rows
