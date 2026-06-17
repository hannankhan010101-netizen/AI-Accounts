"""Last sold/purchased rate lookup — Smart Settings §12.2.7."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from prisma_generated import Prisma

from app.repositories.smart_settings_repository import SmartSettingsRepository

# Smart Settings UI uses SI, VI, SO, PO, etc.
LAST_RATE_DOC_TYPES: frozenset[str] = frozenset({"PO", "QO", "SC", "SI", "SO", "VC", "VI"})

_LEGACY_DOC_TYPE_ALIASES: dict[str, str] = {
    "salesInvoice": "SI",
    "supplierBill": "VI",
    "salesOrder": "SO",
    "purchaseOrder": "PO",
}


def normalize_last_rate_doc_type(doc_type: str) -> str:
    key = (doc_type or "SI").strip()
    return _LEGACY_DOC_TYPE_ALIASES.get(key, key)


class LastRateService:
    def __init__(
        self,
        *,
        prisma: Prisma,
        smart_settings_repository: SmartSettingsRepository,
    ) -> None:
        self._db = prisma
        self._smart = smart_settings_repository

    async def _last_rate_enabled(
        self, *, company_id: str, doc_type: str, mode: str
    ) -> bool:
        row = await self._smart.get_for_company(company_id=company_id)
        if row is None:
            return False
        payload = row.payload if isinstance(row.payload, dict) else {}
        last_rate = payload.get("lastRate") or {}
        if not isinstance(last_rate, dict):
            return False
        block = last_rate.get(doc_type) or {}
        if not isinstance(block, dict):
            return False
        return bool(block.get(mode))

    async def lookup(
        self,
        *,
        company_id: str,
        party_id: str,
        product_code: str,
        doc_type: str = "SI",
        for_edit: bool = True,
    ) -> dict[str, Any] | None:
        """Resolve last rate for a party + product when enabled in Smart Settings."""

        normalized = normalize_last_rate_doc_type(doc_type)
        mode = "addEdit" if for_edit else "view"
        if not await self._last_rate_enabled(
            company_id=company_id, doc_type=normalized, mode=mode
        ):
            return None
        if not product_code.strip():
            return None

        if normalized == "QO":
            return await self._from_quotations(
                company_id=company_id,
                customer_id=party_id,
                product_code=product_code,
            )
        if normalized in {"SI", "SC"}:
            return await self._from_sales_invoices(
                company_id=company_id,
                customer_id=party_id,
                product_code=product_code,
            )
        if normalized == "SO":
            return await self._from_sales_orders(
                company_id=company_id,
                customer_id=party_id,
                product_code=product_code,
            )
        if normalized in {"VI", "VC"}:
            return await self._from_supplier_bills(
                company_id=company_id,
                supplier_id=party_id,
                product_code=product_code,
            )
        if normalized == "PO":
            return await self._from_purchase_orders(
                company_id=company_id,
                supplier_id=party_id,
                product_code=product_code,
            )
        return None

    async def sales_last_rate(
        self,
        *,
        company_id: str,
        customer_id: str,
        product_code: str,
        doc_type: str = "SI",
        for_edit: bool = True,
    ) -> dict[str, Any] | None:
        return await self.lookup(
            company_id=company_id,
            party_id=customer_id,
            product_code=product_code,
            doc_type=doc_type,
            for_edit=for_edit,
        )

    async def purchase_last_rate(
        self,
        *,
        company_id: str,
        supplier_id: str,
        product_code: str,
        doc_type: str = "VI",
        for_edit: bool = True,
    ) -> dict[str, Any] | None:
        return await self.lookup(
            company_id=company_id,
            party_id=supplier_id,
            product_code=product_code,
            doc_type=doc_type,
            for_edit=for_edit,
        )

    async def _from_quotations(
        self, *, company_id: str, customer_id: str, product_code: str
    ) -> dict[str, Any] | None:
        quotes = await self._db.quotation.find_many(
            where={"companyId": company_id, "customerId": customer_id},
            order={"quotationDate": "desc"},
            include={"lines": True},
            take=50,
        )
        for quote in quotes:
            for line in quote.lines or []:
                if line.productCode == product_code:
                    return self._line_payload(
                        rate=line.rate,
                        gst_code=line.gstCode,
                        gst_rate=line.gstRate,
                        document_id=quote.id,
                        document_number=quote.quotationNumber,
                        document_date=quote.quotationDate,
                        document_label="quotation",
                    )
        return None

    async def _from_sales_invoices(
        self, *, company_id: str, customer_id: str, product_code: str
    ) -> dict[str, Any] | None:
        invoices = await self._db.salesinvoice.find_many(
            where={"companyId": company_id, "customerId": customer_id},
            order={"invoiceDate": "desc"},
            include={"lines": True},
            take=50,
        )
        for inv in invoices:
            for line in inv.lines or []:
                if line.productCode == product_code:
                    return self._line_payload(
                        rate=line.rate,
                        gst_code=line.gstCode,
                        gst_rate=line.gstRate,
                        document_id=inv.id,
                        document_number=inv.invoiceNumber,
                        document_date=inv.invoiceDate,
                        document_label="invoice",
                    )
        return None

    async def _from_sales_orders(
        self, *, company_id: str, customer_id: str, product_code: str
    ) -> dict[str, Any] | None:
        orders = await self._db.salesorder.find_many(
            where={"companyId": company_id, "customerId": customer_id},
            order={"orderDate": "desc"},
            include={"lines": True},
            take=50,
        )
        for order in orders:
            for line in order.lines or []:
                if line.productCode == product_code:
                    return self._line_payload(
                        rate=line.rate,
                        gst_code=getattr(line, "gstCode", None),
                        gst_rate=getattr(line, "gstRate", None),
                        document_id=order.id,
                        document_number=order.orderNumber,
                        document_date=order.orderDate,
                        document_label="order",
                    )
        return None

    async def _from_supplier_bills(
        self, *, company_id: str, supplier_id: str, product_code: str
    ) -> dict[str, Any] | None:
        bills = await self._db.supplierbill.find_many(
            where={"companyId": company_id, "supplierId": supplier_id},
            order={"billDate": "desc"},
            include={"lines": True},
            take=50,
        )
        for bill in bills:
            for line in bill.lines or []:
                if line.productCode == product_code:
                    return self._line_payload(
                        rate=line.rate,
                        gst_code=line.gstCode,
                        gst_rate=line.gstRate,
                        document_id=bill.id,
                        document_number=bill.billNumber,
                        document_date=bill.billDate,
                        document_label="bill",
                    )
        return None

    async def _from_purchase_orders(
        self, *, company_id: str, supplier_id: str, product_code: str
    ) -> dict[str, Any] | None:
        orders = await self._db.purchaseorder.find_many(
            where={"companyId": company_id, "supplierId": supplier_id},
            order={"orderDate": "desc"},
            include={"lines": True},
            take=50,
        )
        for order in orders:
            for line in order.lines or []:
                if line.productCode == product_code:
                    return self._line_payload(
                        rate=line.rate,
                        gst_code=getattr(line, "gstCode", None),
                        gst_rate=getattr(line, "gstRate", None),
                        document_id=order.id,
                        document_number=order.orderNumber,
                        document_date=order.orderDate,
                        document_label="order",
                    )
        return None

    @staticmethod
    def _line_payload(
        *,
        rate: Decimal,
        gst_code: str | None,
        gst_rate: Decimal | None,
        document_id: str,
        document_number: str | None,
        document_date: datetime,
        document_label: str,
    ) -> dict[str, Any]:
        return {
            "rate": str(rate),
            "gstCode": gst_code,
            "gstRate": str(gst_rate) if gst_rate is not None else None,
            "documentId": document_id,
            "documentNumber": document_number,
            "documentDate": document_date.isoformat(),
            "documentLabel": document_label,
            # Back-compat keys used by existing clients
            "invoiceId": document_id if document_label == "invoice" else None,
            "invoiceNumber": document_number if document_label == "invoice" else None,
            "invoiceDate": document_date.isoformat() if document_label == "invoice" else None,
            "billId": document_id if document_label == "bill" else None,
            "billNumber": document_number if document_label == "bill" else None,
            "billDate": document_date.isoformat() if document_label == "bill" else None,
        }
