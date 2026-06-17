"""Central posting orchestration — P0 accounting foundation.

All GL effects for approvable documents flow through this service so
posting rules, prerequisites, and journal traceability stay consistent.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from prisma_generated.models import GoodsIssue, Journal, SalesInvoice, SupplierBill

from app.core.exceptions import ValidationAppError
from app.domain import document_workflow as wf
from app.repositories.goods_issue_repository import GoodsIssueRepository
from app.repositories.inventory_repository import StockAdjustmentRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.sales_invoice_repository import SalesInvoiceRepository
from app.repositories.supplier_bill_repository import SupplierBillRepository
from app.services.document_number_service import DocumentNumberService
from app.services.posting_prerequisites_service import PostingPrerequisitesService
from app.services.inventory_quantity_service import InventoryQuantityService
from app.services.posting_service import PostingService
from app.services.tax_calculation_service import TaxCalculationService


class PostingEngine:
    """Approve drafts and post inventory movements to the GL."""

    def __init__(
        self,
        *,
        posting_service: PostingService,
        prerequisites: PostingPrerequisitesService,
        sales_invoice_repository: SalesInvoiceRepository,
        supplier_bill_repository: SupplierBillRepository,
        stock_adjustment_repository: StockAdjustmentRepository,
        tax_calculation_service: TaxCalculationService,
        product_repository: ProductRepository,
        goods_issue_repository: GoodsIssueRepository,
        document_number_service: DocumentNumberService,
        inventory_quantity_service: InventoryQuantityService | None = None,
    ) -> None:
        self._posting = posting_service
        self._prereq = prerequisites
        self._invoices = sales_invoice_repository
        self._bills = supplier_bill_repository
        self._adjustments = stock_adjustment_repository
        self._tax = tax_calculation_service
        self._products = product_repository
        self._goods_issues = goods_issue_repository
        self._numbers = document_number_service
        self._inventory_qty = inventory_quantity_service

    async def approve_sales_invoice(
        self,
        *,
        company_id: str,
        invoice_id: str,
    ) -> SalesInvoice:
        invoice = await self._invoices.get_invoice(
            company_id=company_id, invoice_id=invoice_id
        )
        if invoice is None:
            raise ValidationAppError("Sales invoice not found")
        if invoice.journalId:
            raise ValidationAppError("Sales invoice is already posted to the GL")
        wf.assert_can_transition(current=invoice.status, target=wf.POSTED)

        await self._prereq.require_sales_invoice_posting(company_id=company_id)

        raw_lines = [
            {
                "productCode": line.productCode,
                "quantity": line.quantity,
                "rate": line.rate,
                "gstCode": line.gstCode,
                "gstRate": line.gstRate,
            }
            for line in invoice.lines or []
        ]
        taxed = await self._tax.compute_sales_lines(
            company_id=company_id, raw_lines=raw_lines
        )
        correlation_id = str(uuid.uuid4())
        journal = await self._posting.post_sales_invoice(
            company_id=company_id,
            invoice_date=invoice.invoiceDate,
            invoice_number=invoice.invoiceNumber,
            net_amount=taxed.net_total,
            gross_amount=taxed.gross_total,
            tax_legs=taxed.tax_legs,
            source_id=invoice.id,
            correlation_id=correlation_id,
        )
        if journal is None:
            raise ValidationAppError("Sales invoice posting failed unexpectedly")

        return await self._invoices.mark_posted(
            company_id=company_id,
            invoice_id=invoice_id,
            journal_id=journal.id,
        )

    async def issue_goods_for_invoice(
        self,
        *,
        company_id: str,
        invoice_id: str,
        issue_date: datetime | None = None,
    ) -> GoodsIssue:
        """Post COGS / inventory relief via a goods issue voucher (P2)."""

        invoice = await self._invoices.get_invoice(
            company_id=company_id, invoice_id=invoice_id
        )
        if invoice is None:
            raise ValidationAppError("Sales invoice not found")
        if invoice.status != wf.POSTED or not invoice.journalId:
            raise ValidationAppError("Sales invoice must be posted before goods issue")
        existing = await self._goods_issues.get_by_invoice(
            company_id=company_id, sales_invoice_id=invoice_id
        )
        if existing is not None:
            raise ValidationAppError("Goods issue already exists for this invoice")

        line_payloads, cogs_total, stock_codes = await self._build_cogs_lines(
            company_id=company_id, invoice=invoice
        )
        if cogs_total <= 0:
            raise ValidationAppError(
                "No stock lines with positive cost to issue"
            )

        d = await self._prereq.require_cogs_posting(company_id=company_id)
        cogs_code = d["cogsNominalCode"]
        inv_code = d["inventoryNominalCode"]
        when = issue_date or invoice.invoiceDate
        correlation_id = str(uuid.uuid4())
        journal = await self._posting.create_traced_journal(
            company_id=company_id,
            journal_date=when,
            ref_no=f"COGS {invoice.invoiceNumber}",
            lines=[
                {"nominalCode": cogs_code, "debit": cogs_total, "credit": Decimal(0)},
                {"nominalCode": inv_code, "debit": Decimal(0), "credit": cogs_total},
            ],
            source_type=wf.SOURCE_GOODS_ISSUE,
            source_id=invoice.id,
            correlation_id=correlation_id,
        )
        if self._inventory_qty is not None and stock_codes:
            await self._inventory_qty.apply_goods_issue_invoice_lines(
                company_id=company_id,
                invoice_lines=invoice.lines or [],
                stock_product_codes=stock_codes,
            )
        voucher_number = str(
            await self._numbers.reserve_next(company_id=company_id, sequence_key="GI")
        )
        return await self._goods_issues.create_issue(
            company_id=company_id,
            voucher_number=voucher_number,
            issue_date=when,
            sales_invoice_id=invoice.id,
            lines=line_payloads,
            journal_id=journal.id,
        )

    async def _build_cogs_lines(
        self, *, company_id: str, invoice: SalesInvoice
    ) -> tuple[list[dict], Decimal, set[str]]:
        codes = [
            line.productCode
            for line in (invoice.lines or [])
            if line.productCode
        ]
        if not codes:
            return [], Decimal(0), set()
        products = await self._products.get_by_codes(
            company_id=company_id, codes=codes
        )
        by_code = {p.code: p for p in products}
        cogs_total = Decimal(0)
        line_payloads: list[dict] = []
        stock_codes: set[str] = set()
        for line in invoice.lines or []:
            if not line.productCode:
                continue
            prod = by_code.get(line.productCode)
            if prod is None or not prod.isStock:
                continue
            qty = Decimal(str(line.quantity))
            cost = Decimal(str(prod.cost))
            if cost <= 0:
                continue
            cogs_total += qty * cost
            stock_codes.add(line.productCode)
            payload: dict = {
                "productCode": line.productCode,
                "quantity": qty,
                "unitCost": cost,
            }
            if getattr(line, "batchNumber", None):
                payload["batchNumber"] = line.batchNumber
            line_payloads.append(payload)
        return line_payloads, cogs_total, stock_codes

    async def approve_supplier_bill(
        self,
        *,
        company_id: str,
        bill_id: str,
    ) -> SupplierBill:
        bill = await self._bills.get_bill(company_id=company_id, bill_id=bill_id)
        if bill is None:
            raise ValidationAppError("Supplier bill not found")
        if bill.journalId:
            raise ValidationAppError("Supplier bill is already posted to the GL")
        wf.assert_can_transition(current=bill.status, target=wf.POSTED)

        await self._prereq.require_supplier_bill_posting(company_id=company_id)

        raw_lines = [
            {
                "productCode": line.productCode,
                "quantity": line.quantity,
                "rate": line.rate,
                "gstCode": line.gstCode,
                "gstRate": line.gstRate,
            }
            for line in bill.lines or []
        ]
        taxed = await self._tax.compute_purchase_lines(
            company_id=company_id, raw_lines=raw_lines
        )
        correlation_id = str(uuid.uuid4())
        journal = await self._posting.post_supplier_bill(
            company_id=company_id,
            bill_date=bill.billDate,
            bill_number=bill.billNumber,
            net_amount=taxed.net_total,
            gross_amount=taxed.gross_total,
            tax_legs=taxed.tax_legs,
            source_id=bill.id,
            correlation_id=correlation_id,
        )
        if journal is None:
            raise ValidationAppError("Supplier bill posting failed unexpectedly")

        return await self._bills.mark_posted(
            company_id=company_id,
            bill_id=bill_id,
            journal_id=journal.id,
        )

    async def post_stock_adjustment(
        self,
        *,
        company_id: str,
        adjustment_id: str,
    ) -> Journal:
        """Post inventory adjustment: net increase DR inventory / CR variance; decrease inverse."""

        adj = await self._adjustments.get_adjustment(
            company_id=company_id, adjustment_id=adjustment_id
        )
        if adj is None:
            raise ValidationAppError("Stock adjustment not found")
        if adj.journalId:
            raise ValidationAppError("Stock adjustment is already posted to the GL")

        d = await self._prereq.require_stock_adjustment_posting(company_id=company_id)
        inventory_code = d["inventoryNominalCode"]
        variance_code = d["stockAdjustmentNominalCode"]

        total_value = Decimal(0)
        for line in adj.lines or []:
            delta = Decimal(str(line.quantityDelta))
            cost = Decimal(str(line.unitCost))
            total_value += delta * cost

        if total_value == 0:
            raise ValidationAppError(
                "Stock adjustment has zero value; set unit costs on lines before posting"
            )

        if total_value > 0:
            journal_lines = [
                {
                    "nominalCode": inventory_code,
                    "debit": total_value,
                    "credit": Decimal(0),
                },
                {
                    "nominalCode": variance_code,
                    "debit": Decimal(0),
                    "credit": total_value,
                },
            ]
        else:
            amount = abs(total_value)
            journal_lines = [
                {
                    "nominalCode": variance_code,
                    "debit": amount,
                    "credit": Decimal(0),
                },
                {
                    "nominalCode": inventory_code,
                    "debit": Decimal(0),
                    "credit": amount,
                },
            ]

        correlation_id = str(uuid.uuid4())
        journal = await self._posting.create_traced_journal(
            company_id=company_id,
            journal_date=adj.adjustmentDate,
            ref_no=f"SA {adj.voucherNumber}",
            lines=journal_lines,
            source_type=wf.SOURCE_STOCK_ADJUSTMENT,
            source_id=adj.id,
            correlation_id=correlation_id,
        )
        await self._adjustments.mark_posted(
            company_id=company_id,
            adjustment_id=adjustment_id,
            journal_id=journal.id,
        )
        if self._inventory_qty is not None:
            await self._inventory_qty.apply_stock_adjustment_lines(
                company_id=company_id,
                lines=adj.lines or [],
            )
        return journal
