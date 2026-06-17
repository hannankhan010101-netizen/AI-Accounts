"""Document conversion — catalog §5.3, §6.2.

- Quotation → Sales Order (no GL; quotation status becomes ``converted``)
- Sales Order → Sales Invoice (posts AR journal; SO status becomes ``invoiced``)
- Purchase Order → Supplier Bill (posts AP journal; PO status becomes ``billed``)

Each conversion copies the source lines into the destination header, reserves
the next document number from the appropriate sequence, and routes the
destination through the existing posting service so the GL stays consistent.
"""

from __future__ import annotations

from app.core.exceptions import ValidationAppError
from app.repositories.purchase_order_repository import PurchaseOrderRepository
from app.repositories.quotation_repository import QuotationRepository
from app.repositories.sales_invoice_repository import SalesInvoiceRepository
from app.repositories.sales_order_repository import SalesOrderRepository
from app.repositories.supplier_bill_repository import SupplierBillRepository
from app.services.document_number_service import DocumentNumberService
from app.services.lock_date_service import LockDateService
from app.services.posting_engine import PostingEngine


class ConversionService:
    """Orchestrates Quote → SO → Invoice and PO → Bill."""

    def __init__(
        self,
        *,
        quotation_repository: QuotationRepository,
        sales_order_repository: SalesOrderRepository,
        sales_invoice_repository: SalesInvoiceRepository,
        purchase_order_repository: PurchaseOrderRepository,
        supplier_bill_repository: SupplierBillRepository,
        document_number_service: DocumentNumberService,
        lock_date_service: LockDateService,
        posting_engine: PostingEngine,
    ) -> None:
        self._quotations = quotation_repository
        self._sales_orders = sales_order_repository
        self._sales_invoices = sales_invoice_repository
        self._purchase_orders = purchase_order_repository
        self._supplier_bills = supplier_bill_repository
        self._numbers = document_number_service
        self._lock_date = lock_date_service
        self._posting_engine = posting_engine

    async def quotation_to_sales_order(
        self,
        *,
        company_id: str,
        quotation_id: str,
    ) -> dict:
        """Copy quotation lines into a new sales order; mark the quote ``converted``."""

        quote = await self._quotations.get_quotation(
            company_id=company_id,
            quotation_id=quotation_id,
        )
        if quote is None:
            raise ValidationAppError("Quotation not found")
        if quote.status in {"converted", "rejected"}:
            raise ValidationAppError(
                f"Quotation is {quote.status}; only draft/approved/accepted quotes can convert."
            )

        await self._lock_date.assert_not_locked(
            company_id=company_id,
            document_date=quote.quotationDate,
            document_label="sales order",
        )

        order_number = str(
            await self._numbers.reserve_next(company_id=company_id, sequence_key="SO")
        )
        order_lines = _copy_lines(quote.lines)
        order = await self._sales_orders.create_order(
            company_id=company_id,
            order_number=order_number,
            order_date=quote.quotationDate,
            customer_id=quote.customerId,
            lines=order_lines,
        )
        await self._quotations.update_status(
            company_id=company_id, quotation_id=quotation_id, status="converted"
        )
        return {"salesOrder": order, "quotationId": quotation_id}

    async def sales_order_to_invoice(
        self,
        *,
        company_id: str,
        order_id: str,
    ) -> dict:
        """Copy SO lines into a new sales invoice and post the AR journal."""

        order = await self._sales_orders.get_order(
            company_id=company_id, order_id=order_id
        )
        if order is None:
            raise ValidationAppError("Sales order not found")
        if order.status not in {"approved", "in_progress"}:
            raise ValidationAppError(
                f"Sales order is {order.status}; only approved/in-progress orders can convert."
            )

        await self._lock_date.assert_not_locked(
            company_id=company_id,
            document_date=order.orderDate,
            document_label="sales invoice",
        )

        invoice_number = str(
            await self._numbers.reserve_next(company_id=company_id, sequence_key="SI")
        )
        invoice_lines = _copy_lines(order.lines)
        invoice = await self._sales_invoices.create_invoice(
            company_id=company_id,
            invoice_number=invoice_number,
            invoice_date=order.orderDate,
            customer_id=order.customerId,
            lines=invoice_lines,
            journal_id=None,
        )
        try:
            invoice = await self._posting_engine.approve_sales_invoice(
                company_id=company_id, invoice_id=invoice.id
            )
            posted = True
        except ValidationAppError:
            posted = False
        await self._sales_orders.update_status(
            company_id=company_id, order_id=order_id, status="invoiced"
        )
        return {
            "salesInvoice": invoice,
            "orderId": order_id,
            "posted": posted,
        }

    async def purchase_order_to_bill(
        self,
        *,
        company_id: str,
        order_id: str,
    ) -> dict:
        """Copy PO lines into a new supplier bill and post the AP journal."""

        order = await self._purchase_orders.get_order(
            company_id=company_id, order_id=order_id
        )
        if order is None:
            raise ValidationAppError("Purchase order not found")
        if order.status not in {"approved", "in_progress"}:
            raise ValidationAppError(
                f"Purchase order is {order.status}; only approved/in-progress orders can convert."
            )

        await self._lock_date.assert_not_locked(
            company_id=company_id,
            document_date=order.orderDate,
            document_label="supplier bill",
        )

        bill_number = str(
            await self._numbers.reserve_next(company_id=company_id, sequence_key="VI")
        )
        bill_lines = _copy_lines(order.lines)
        bill = await self._supplier_bills.create_bill(
            company_id=company_id,
            bill_number=bill_number,
            bill_date=order.orderDate,
            supplier_id=order.supplierId,
            lines=bill_lines,
            journal_id=None,
        )
        try:
            bill = await self._posting_engine.approve_supplier_bill(
                company_id=company_id, bill_id=bill.id
            )
            posted = True
        except ValidationAppError:
            posted = False
        await self._purchase_orders.update_status(
            company_id=company_id, order_id=order_id, status="billed"
        )
        return {
            "supplierBill": bill,
            "orderId": order_id,
            "posted": posted,
        }


def _copy_lines(source_lines: list) -> list[dict]:
    """Strip ids; preserve product, qty, rate, tax fields, and project."""

    out: list[dict] = []
    for line in source_lines or []:
        payload: dict = {
            "productCode": getattr(line, "productCode", None),
            "quantity": line.quantity,
            "rate": line.rate,
            "lineTotal": line.lineTotal,
        }
        if hasattr(line, "lineSubtotal"):
            payload["lineSubtotal"] = line.lineSubtotal
        if hasattr(line, "gstCode"):
            payload["gstCode"] = getattr(line, "gstCode", None)
        if hasattr(line, "gstRate"):
            payload["gstRate"] = getattr(line, "gstRate", None)
        if hasattr(line, "taxAmount"):
            payload["taxAmount"] = getattr(line, "taxAmount", None)
        if hasattr(line, "projectCode"):
            payload["projectCode"] = getattr(line, "projectCode", None)
        out.append(payload)
    return out
