"""Void credits/invoices and reverse posted stock adjustments — P16/P17."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from app.core.exceptions import ValidationAppError
from app.domain import document_workflow as wf
from app.repositories.delivery_repository import (
    DeliveryNoteRepository,
    GoodsReceiptNoteRepository,
)
from app.repositories.goods_issue_repository import GoodsIssueRepository
from app.repositories.inventory_repository import StockAdjustmentRepository
from app.repositories.sales_credit_repository import SalesCreditRepository
from app.repositories.sales_invoice_repository import SalesInvoiceRepository
from app.repositories.supplier_bill_repository import SupplierBillRepository
from app.repositories.supplier_credit_repository import SupplierCreditRepository
from app.services.inventory_quantity_service import InventoryQuantityService
from app.services.journal_service import JournalService
from app.services.posting_prerequisites_service import PostingPrerequisitesService


class DocumentReversalService:
    def __init__(
        self,
        *,
        sales_credits: SalesCreditRepository,
        supplier_credits: SupplierCreditRepository,
        sales_invoices: SalesInvoiceRepository,
        supplier_bills: SupplierBillRepository,
        stock_adjustments: StockAdjustmentRepository,
        goods_issues: GoodsIssueRepository,
        grn_repository: GoodsReceiptNoteRepository,
        delivery_notes: DeliveryNoteRepository,
        journal_service: JournalService,
        inventory_quantities: InventoryQuantityService,
        posting_prerequisites: PostingPrerequisitesService,
    ) -> None:
        self._sales_credits = sales_credits
        self._supplier_credits = supplier_credits
        self._sales_invoices = sales_invoices
        self._supplier_bills = supplier_bills
        self._adjustments = stock_adjustments
        self._goods_issues = goods_issues
        self._grn = grn_repository
        self._delivery = delivery_notes
        self._journals = journal_service
        self._inventory = inventory_quantities
        self._prereq = posting_prerequisites

    async def void_sales_credit(
        self,
        *,
        company_id: str,
        credit_id: str,
        reversal_date: datetime | None = None,
    ) -> dict:
        credit = await self._sales_credits.get_credit(
            company_id=company_id, credit_id=credit_id
        )
        if credit is None:
            raise ValidationAppError("Sales credit not found")
        try:
            wf.assert_can_transition(current=credit.status, target=wf.VOIDED)
        except ValueError as exc:
            raise ValidationAppError(str(exc)) from exc

        rev_date = reversal_date or datetime.now(timezone.utc)
        reversal_journal_id = None
        if credit.journalId:
            rev = await self._journals.reverse_journal(
                company_id=company_id,
                journal_id=credit.journalId,
                reversal_date=rev_date,
                ref_no=f"VOID SC {credit.creditNumber}",
            )
            reversal_journal_id = rev.id

        row = await self._sales_credits.update_status(
            company_id=company_id,
            credit_id=credit_id,
            status=wf.VOIDED,
        )
        return {
            "credit": row,
            "voided": True,
            "reversalJournalId": reversal_journal_id,
        }

    async def void_supplier_credit(
        self,
        *,
        company_id: str,
        credit_id: str,
        reversal_date: datetime | None = None,
    ) -> dict:
        credit = await self._supplier_credits.get_credit(
            company_id=company_id, credit_id=credit_id
        )
        if credit is None:
            raise ValidationAppError("Supplier credit not found")
        try:
            wf.assert_can_transition(current=credit.status, target=wf.VOIDED)
        except ValueError as exc:
            raise ValidationAppError(str(exc)) from exc

        rev_date = reversal_date or datetime.now(timezone.utc)
        reversal_journal_id = None
        if credit.journalId:
            rev = await self._journals.reverse_journal(
                company_id=company_id,
                journal_id=credit.journalId,
                reversal_date=rev_date,
                ref_no=f"VOID VC {credit.creditNumber}",
            )
            reversal_journal_id = rev.id

        row = await self._supplier_credits.update_status(
            company_id=company_id,
            credit_id=credit_id,
            status=wf.VOIDED,
        )
        return {
            "credit": row,
            "voided": True,
            "reversalJournalId": reversal_journal_id,
        }

    async def void_sales_invoice(
        self,
        *,
        company_id: str,
        invoice_id: str,
        reversal_date: datetime | None = None,
    ) -> dict:
        invoice = await self._sales_invoices.get_invoice(
            company_id=company_id, invoice_id=invoice_id
        )
        if invoice is None:
            raise ValidationAppError("Sales invoice not found")
        if invoice.status != wf.POSTED:
            raise ValidationAppError("Only posted sales invoices can be voided")
        try:
            wf.assert_can_transition(current=invoice.status, target=wf.VOIDED)
        except ValueError as exc:
            raise ValidationAppError(str(exc)) from exc

        rev_date = reversal_date or datetime.now(timezone.utc)
        reversal_journal_ids: list[str] = []
        stock_restored: list[dict[str, str]] = []

        goods_issue = await self._goods_issues.get_by_invoice(
            company_id=company_id, sales_invoice_id=invoice_id
        )
        if goods_issue and goods_issue.journalId:
            gi_rev = await self._journals.reverse_journal(
                company_id=company_id,
                journal_id=goods_issue.journalId,
                reversal_date=rev_date,
                ref_no=f"VOID GI {goods_issue.voucherNumber}",
            )
            reversal_journal_ids.append(gi_rev.id)
            stock_restored = await self._inventory.restore_goods_issue_lines(
                company_id=company_id,
                lines=goods_issue.lines or [],
            )
            await self._goods_issues.update_status(
                company_id=company_id,
                goods_issue_id=goods_issue.id,
                status=wf.VOIDED,
            )

        if invoice.journalId:
            inv_rev = await self._journals.reverse_journal(
                company_id=company_id,
                journal_id=invoice.journalId,
                reversal_date=rev_date,
                ref_no=f"VOID SI {invoice.invoiceNumber}",
            )
            reversal_journal_ids.append(inv_rev.id)

        dgn_side = await self._void_delivery_notes_for_source(
            company_id=company_id,
            source_kind="GDNSI",
            source_id=invoice_id,
        )

        row = await self._sales_invoices.update_status(
            company_id=company_id,
            invoice_id=invoice_id,
            status=wf.VOIDED,
        )
        return {
            "invoice": row,
            "voided": True,
            "reversalJournalIds": reversal_journal_ids,
            "stockRestored": stock_restored,
            "deliveryNotesVoided": dgn_side["deliveryNotesVoided"],
            "deliveryStockRestored": dgn_side["deliveryStockRestored"],
        }

    async def void_supplier_bill(
        self,
        *,
        company_id: str,
        bill_id: str,
        reversal_date: datetime | None = None,
    ) -> dict:
        bill = await self._supplier_bills.get_bill(company_id=company_id, bill_id=bill_id)
        if bill is None:
            raise ValidationAppError("Supplier bill not found")
        if bill.status != wf.POSTED:
            raise ValidationAppError("Only posted supplier bills can be voided")
        try:
            wf.assert_can_transition(current=bill.status, target=wf.VOIDED)
        except ValueError as exc:
            raise ValidationAppError(str(exc)) from exc

        rev_date = reversal_date or datetime.now(timezone.utc)
        reversal_journal_id = None
        if bill.journalId:
            rev = await self._journals.reverse_journal(
                company_id=company_id,
                journal_id=bill.journalId,
                reversal_date=rev_date,
                ref_no=f"VOID VI {bill.billNumber}",
            )
            reversal_journal_id = rev.id

        grn_rollback: list[dict[str, str]] = []
        grn_voided: list[str] = []
        grn_notes = await self._grn.list_by_source(
            company_id=company_id,
            source_kind="GRNVI",
            source_id=bill_id,
        )
        for note in grn_notes:
            if note.status == wf.VOIDED:
                continue
            grn_rollback.extend(
                await self._inventory.reverse_grn_receipt_lines(
                    company_id=company_id,
                    lines=note.lines or [],
                )
            )
            await self._grn.update_status(
                company_id=company_id,
                note_id=note.id,
                status=wf.VOIDED,
            )
            grn_voided.append(note.voucherNumber)

        manual_grn_notes = await self._grn.list_by_source(
            company_id=company_id,
            source_kind="manual",
            source_id=bill_id,
        )
        for note in manual_grn_notes:
            if note.status == wf.VOIDED:
                continue
            grn_rollback.extend(
                await self._inventory.reverse_grn_receipt_lines(
                    company_id=company_id,
                    lines=note.lines or [],
                )
            )
            await self._grn.update_status(
                company_id=company_id,
                note_id=note.id,
                status=wf.VOIDED,
            )
            grn_voided.append(note.voucherNumber)

        row = await self._supplier_bills.update_status(
            company_id=company_id,
            bill_id=bill_id,
            status=wf.VOIDED,
        )
        return {
            "bill": row,
            "voided": True,
            "reversalJournalId": reversal_journal_id,
            "grnVoided": grn_voided,
            "grnStockRollback": grn_rollback,
        }

    async def void_goods_issue_only(
        self,
        *,
        company_id: str,
        invoice_id: str,
        reversal_date: datetime | None = None,
    ) -> dict:
        """Reverse COGS / GI only; leave the sales invoice posted — P18."""

        invoice = await self._sales_invoices.get_invoice(
            company_id=company_id, invoice_id=invoice_id
        )
        if invoice is None:
            raise ValidationAppError("Sales invoice not found")
        if invoice.status != wf.POSTED:
            raise ValidationAppError("Invoice must remain posted; void goods issue only")

        goods_issue = await self._goods_issues.get_by_invoice(
            company_id=company_id, sales_invoice_id=invoice_id
        )
        if goods_issue is None:
            raise ValidationAppError("No goods issue for this invoice")
        if goods_issue.status == wf.VOIDED:
            raise ValidationAppError("Goods issue is already voided")

        rev_date = reversal_date or datetime.now(timezone.utc)
        reversal_journal_id = None
        if goods_issue.journalId:
            rev = await self._journals.reverse_journal(
                company_id=company_id,
                journal_id=goods_issue.journalId,
                reversal_date=rev_date,
                ref_no=f"VOID GI {goods_issue.voucherNumber}",
            )
            reversal_journal_id = rev.id

        stock_restored = await self._inventory.restore_goods_issue_lines(
            company_id=company_id,
            lines=goods_issue.lines or [],
        )
        gi_row = await self._goods_issues.update_status(
            company_id=company_id,
            goods_issue_id=goods_issue.id,
            status=wf.VOIDED,
        )
        return {
            "goodsIssue": gi_row,
            "invoiceId": invoice_id,
            "voidedGoodsIssueOnly": True,
            "reversalJournalId": reversal_journal_id,
            "stockRestored": stock_restored,
        }

    async def _void_delivery_notes_for_source(
        self,
        *,
        company_id: str,
        source_kind: str,
        source_id: str,
    ) -> dict[str, list]:
        voided: list[str] = []
        stock_restored: list[dict[str, str]] = []
        notes = await self._delivery.list_by_source(
            company_id=company_id,
            source_kind=source_kind,
            source_id=source_id,
        )
        for note in notes:
            if note.status == wf.VOIDED:
                continue
            stock_restored.extend(
                await self._inventory.restore_delivery_note_lines(
                    company_id=company_id,
                    lines=note.lines or [],
                )
            )
            await self._delivery.update_status(
                company_id=company_id,
                note_id=note.id,
                status=wf.VOIDED,
            )
            voided.append(note.voucherNumber)
        return {
            "deliveryNotesVoided": voided,
            "deliveryStockRestored": stock_restored,
        }

    async def void_delivery_notes_for_sales_order(
        self,
        *,
        company_id: str,
        order_id: str,
    ) -> dict[str, list]:
        """Void GDNSO delivery notes when a sales order is cancelled — P20/P21."""

        return await self._void_delivery_notes_for_source(
            company_id=company_id,
            source_kind="GDNSO",
            source_id=order_id,
        )

    async def void_delivery_note(
        self,
        *,
        company_id: str,
        note_id: str,
    ) -> dict:
        note = await self._delivery.get_note(company_id=company_id, note_id=note_id)
        if note is None:
            raise ValidationAppError("Delivery note not found")
        if note.status == wf.VOIDED:
            raise ValidationAppError("Delivery note is already voided")
        stock_restored = await self._inventory.restore_delivery_note_lines(
            company_id=company_id,
            lines=note.lines or [],
        )
        row = await self._delivery.update_status(
            company_id=company_id,
            note_id=note_id,
            status=wf.VOIDED,
        )
        return {
            "deliveryNote": row,
            "voided": True,
            "stockRestored": stock_restored,
        }

    async def void_goods_receipt_note(
        self,
        *,
        company_id: str,
        note_id: str,
    ) -> dict:
        """Void a GRN and roll back received stock — P24."""

        note = await self._grn.get_note(company_id=company_id, note_id=note_id)
        if note is None:
            raise ValidationAppError("Goods receipt note not found")
        if note.status == wf.VOIDED:
            raise ValidationAppError("Goods receipt note is already voided")

        stock_rollback = await self._inventory.reverse_grn_receipt_lines(
            company_id=company_id,
            lines=note.lines or [],
        )
        row = await self._grn.update_status(
            company_id=company_id,
            note_id=note_id,
            status=wf.VOIDED,
        )
        return {
            "goodsReceiptNote": row,
            "voided": True,
            "stockRollback": stock_rollback,
        }

    async def void_grns_for_purchase_order(
        self,
        *,
        company_id: str,
        order_id: str,
    ) -> dict[str, list]:
        """Void GRNPO notes and roll back stock when a PO is cancelled — P19."""

        grn_rollback: list[dict[str, str]] = []
        grn_voided: list[str] = []
        grn_notes = await self._grn.list_by_source(
            company_id=company_id,
            source_kind="GRNPO",
            source_id=order_id,
        )
        for note in grn_notes:
            if note.status == wf.VOIDED:
                continue
            grn_rollback.extend(
                await self._inventory.reverse_grn_receipt_lines(
                    company_id=company_id,
                    lines=note.lines or [],
                )
            )
            await self._grn.update_status(
                company_id=company_id,
                note_id=note.id,
                status=wf.VOIDED,
            )
            grn_voided.append(note.voucherNumber)
        return {"grnVoided": grn_voided, "grnStockRollback": grn_rollback}

    async def void_goods_issue_line(
        self,
        *,
        company_id: str,
        invoice_id: str,
        line_id: str,
        reversal_date: datetime | None = None,
    ) -> dict:
        """Partial COGS reversal and stock restore for one GI line — P19."""

        invoice = await self._sales_invoices.get_invoice(
            company_id=company_id, invoice_id=invoice_id
        )
        if invoice is None:
            raise ValidationAppError("Sales invoice not found")
        if invoice.status != wf.POSTED:
            raise ValidationAppError("Invoice must be posted to void a goods issue line")

        goods_issue = await self._goods_issues.get_by_invoice(
            company_id=company_id, sales_invoice_id=invoice_id
        )
        if goods_issue is None:
            raise ValidationAppError("No goods issue for this invoice")
        if goods_issue.status == wf.VOIDED:
            raise ValidationAppError("Goods issue is already fully voided")

        target = next(
            (ln for ln in (goods_issue.lines or []) if ln.id == line_id),
            None,
        )
        if target is None:
            raise ValidationAppError("Goods issue line not found on this invoice")
        qty = Decimal(str(target.quantity))
        if qty <= 0:
            raise ValidationAppError("Goods issue line is already voided")

        unit_cost = Decimal(str(target.unitCost))
        line_cogs = qty * unit_cost
        if line_cogs <= 0:
            raise ValidationAppError("Line has no COGS amount to reverse")

        rev_date = reversal_date or datetime.now(timezone.utc)
        d = await self._prereq.require_cogs_posting(company_id=company_id)
        partial_rev = await self._journals.create_journal(
            company_id=company_id,
            journal_date=rev_date,
            ref_no=f"VOID GI LINE {goods_issue.voucherNumber}",
            lines=[
                {
                    "nominalCode": d["inventoryNominalCode"],
                    "debit": line_cogs,
                    "credit": Decimal(0),
                },
                {
                    "nominalCode": d["cogsNominalCode"],
                    "debit": Decimal(0),
                    "credit": line_cogs,
                },
            ],
            source_type="GOODS_ISSUE_LINE_VOID",
            source_id=line_id,
        )

        stock_restored = await self._inventory.restore_goods_issue_lines(
            company_id=company_id,
            lines=[target],
        )
        gi_row = await self._goods_issues.zero_line_quantity(
            company_id=company_id, line_id=line_id
        )
        if gi_row is None:
            raise ValidationAppError("Goods issue line not found")

        all_zero = all(
            Decimal(str(ln.quantity)) <= 0 for ln in (gi_row.lines or [])
        )
        if all_zero:
            gi_row = await self._goods_issues.update_status(
                company_id=company_id,
                goods_issue_id=gi_row.id,
                status=wf.VOIDED,
            )

        return {
            "goodsIssue": gi_row,
            "invoiceId": invoice_id,
            "lineId": line_id,
            "partialReversalJournalId": partial_rev.id,
            "lineCogsReversed": str(line_cogs),
            "stockRestored": stock_restored,
            "goodsIssueFullyVoided": all_zero,
        }

    async def repost_remaining_goods_issue_cogs(
        self,
        *,
        company_id: str,
        invoice_id: str,
        journal_date: datetime | None = None,
    ) -> dict:
        """Replace the header COGS journal with the sum of remaining GI lines — P20."""

        goods_issue = await self._goods_issues.get_by_invoice(
            company_id=company_id, sales_invoice_id=invoice_id
        )
        if goods_issue is None:
            raise ValidationAppError("No goods issue for this invoice")
        if goods_issue.status == wf.VOIDED:
            raise ValidationAppError("Goods issue is voided")

        remaining_cogs = Decimal(0)
        for ln in goods_issue.lines or []:
            qty = Decimal(str(ln.quantity))
            if qty <= 0:
                continue
            remaining_cogs += qty * Decimal(str(ln.unitCost))

        if remaining_cogs <= 0:
            raise ValidationAppError("No remaining COGS to post")

        when = journal_date or datetime.now(timezone.utc)
        reversal_journal_id = None
        if goods_issue.journalId:
            rev = await self._journals.reverse_journal(
                company_id=company_id,
                journal_id=goods_issue.journalId,
                reversal_date=when,
                ref_no=f"REPOST GI {goods_issue.voucherNumber}",
            )
            reversal_journal_id = rev.id

        d = await self._prereq.require_cogs_posting(company_id=company_id)
        new_journal = await self._journals.create_journal(
            company_id=company_id,
            journal_date=when,
            ref_no=f"COGS REMAINING {goods_issue.voucherNumber}",
            lines=[
                {
                    "nominalCode": d["cogsNominalCode"],
                    "debit": remaining_cogs,
                    "credit": Decimal(0),
                },
                {
                    "nominalCode": d["inventoryNominalCode"],
                    "debit": Decimal(0),
                    "credit": remaining_cogs,
                },
            ],
            source_type="GOODS_ISSUE_REPOST",
            source_id=goods_issue.id,
        )
        gi_row = await self._goods_issues.update_journal_id(
            company_id=company_id,
            goods_issue_id=goods_issue.id,
            journal_id=new_journal.id,
        )
        return {
            "goodsIssue": gi_row,
            "invoiceId": invoice_id,
            "remainingCogsPosted": str(remaining_cogs),
            "priorJournalReversalId": reversal_journal_id,
            "cogsJournalId": new_journal.id,
        }

    async def reverse_stock_adjustment(
        self,
        *,
        company_id: str,
        adjustment_id: str,
        reversal_date: datetime | None = None,
    ) -> dict:
        adj = await self._adjustments.get_adjustment(
            company_id=company_id, adjustment_id=adjustment_id
        )
        if adj is None:
            raise ValidationAppError("Stock adjustment not found")
        if not adj.journalId:
            raise ValidationAppError("Stock adjustment is not posted to the GL")
        try:
            wf.assert_can_transition(current=adj.status, target=wf.REVERSED)
        except ValueError as exc:
            raise ValidationAppError(str(exc)) from exc

        rev_date = reversal_date or datetime.now(timezone.utc)
        stock_rollback = await self._inventory.apply_stock_adjustment_lines(
            company_id=company_id,
            lines=adj.lines or [],
            multiplier=Decimal("-1"),
        )
        rev = await self._journals.reverse_journal(
            company_id=company_id,
            journal_id=adj.journalId,
            reversal_date=rev_date,
            ref_no=f"REV SA {adj.voucherNumber}",
        )
        row = await self._adjustments.update_status(
            company_id=company_id,
            adjustment_id=adjustment_id,
            status=wf.REVERSED,
        )
        return {
            "adjustment": row,
            "reversed": True,
            "reversalJournalId": rev.id,
            "stockRollback": stock_rollback,
        }
