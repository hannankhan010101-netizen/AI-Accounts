"""Prevent duplicate stock paths for sales delivery and purchase receipt — P22/P23."""

from __future__ import annotations

from app.core.exceptions import ValidationAppError
from app.domain import document_workflow as wf
from app.repositories.delivery_repository import (
    DeliveryNoteRepository,
    GoodsReceiptNoteRepository,
)
from app.repositories.goods_issue_repository import GoodsIssueRepository


class InventoryStockGuardService:
    def __init__(
        self,
        *,
        delivery_notes: DeliveryNoteRepository,
        goods_issues: GoodsIssueRepository,
        grn_repository: GoodsReceiptNoteRepository,
    ) -> None:
        self._delivery = delivery_notes
        self._goods_issues = goods_issues
        self._grn = grn_repository

    async def assert_delivery_stock_allowed(
        self,
        *,
        company_id: str,
        source_kind: str,
        source_id: str | None,
        skip_stock_movement: bool,
    ) -> None:
        """Block a second GDNSI delivery with stock unless ``skipStockMovement``."""

        if skip_stock_movement or source_kind != "GDNSI" or not source_id:
            return

        notes = await self._delivery.list_by_source(
            company_id=company_id,
            source_kind="GDNSI",
            source_id=source_id,
        )
        if any(n.status != wf.VOIDED for n in notes):
            raise ValidationAppError(
                "A non-voided delivery note already exists for this invoice; "
                "void it first or set skipStockMovement=true for a non-stock delivery record"
            )

        goods_issue = await self._goods_issues.get_by_invoice(
            company_id=company_id,
            sales_invoice_id=source_id,
        )
        if goods_issue is not None and goods_issue.status != wf.VOIDED:
            raise ValidationAppError(
                "Goods issue already exists for this invoice; use skipStockMovement=true "
                "on the delivery note if you only need a delivery document without extra stock relief"
            )

    async def assert_goods_issue_allowed(
        self,
        *,
        company_id: str,
        invoice_id: str,
        skip_stock_movement: bool,
    ) -> None:
        """Block goods issue when a GDNSI delivery already moved stock (unless skipped)."""

        if skip_stock_movement:
            return

        notes = await self._delivery.list_by_source(
            company_id=company_id,
            source_kind="GDNSI",
            source_id=invoice_id,
        )
        if any(n.status != wf.VOIDED for n in notes):
            raise ValidationAppError(
                "Non-voided delivery note(s) exist for this invoice; void them first or pass "
                "skipStockMovement=true on goods issue when COGS should post without conflicting stock"
            )

    async def assert_grn_receipt_allowed(
        self,
        *,
        company_id: str,
        source_kind: str,
        source_id: str | None,
        skip_stock_movement: bool,
    ) -> None:
        """Block duplicate GRNPO/GRNVI receipts unless ``skipStockMovement`` — P23."""

        if skip_stock_movement or not source_id:
            return
        if source_kind not in {"GRNPO", "GRNVI", "manual"}:
            return

        notes = await self._grn.list_by_source(
            company_id=company_id,
            source_kind=source_kind,
            source_id=source_id,
        )
        if any(n.status != wf.VOIDED for n in notes):
            labels = {
                "GRNPO": "purchase order",
                "GRNVI": "supplier bill",
                "manual": "source document",
            }
            label = labels.get(source_kind, source_kind)
            raise ValidationAppError(
                f"A non-voided goods receipt note already exists for this {label}; "
                "void it first or set skipStockMovement=true for a non-stock GRN record"
            )
