"""Product batch quantity adjustments — P17."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from app.repositories.inventory_repository import ProductBatchRepository


class InventoryQuantityService:
    def __init__(self, *, batches: ProductBatchRepository) -> None:
        self._batches = batches

    async def apply_stock_adjustment_lines(
        self,
        *,
        company_id: str,
        lines: list[Any],
        multiplier: Decimal = Decimal("1"),
    ) -> list[dict[str, str]]:
        """Apply ``quantityDelta`` to product batches (``multiplier=-1`` rolls back)."""

        applied: list[dict[str, str]] = []
        for line in lines:
            code = getattr(line, "productCode", None)
            if not code:
                continue
            delta = Decimal(str(getattr(line, "quantityDelta", 0))) * multiplier
            if delta == 0:
                continue
            batch = await self._batches.apply_product_delta(
                company_id=company_id,
                product_code=str(code),
                delta=delta,
            )
            applied.append(
                {
                    "productCode": str(code),
                    "batchNumber": batch.batchNumber,
                    "quantityDelta": str(delta),
                }
            )
        return applied

    async def restore_goods_issue_lines(
        self,
        *,
        company_id: str,
        lines: list[Any],
    ) -> list[dict[str, str]]:
        """Add issued quantities back to stock when voiding a sales invoice."""

        restored: list[dict[str, str]] = []
        for line in lines:
            code = getattr(line, "productCode", None)
            if not code:
                continue
            qty = Decimal(str(getattr(line, "quantity", 0)))
            if qty <= 0:
                continue
            batch_number = getattr(line, "batchNumber", None)
            batch = await self._batches.apply_product_delta(
                company_id=company_id,
                product_code=str(code),
                delta=qty,
                batch_number=str(batch_number) if batch_number else None,
            )
            restored.append(
                {
                    "productCode": str(code),
                    "batchNumber": batch.batchNumber,
                    "quantityRestored": str(qty),
                }
            )
        return restored

    async def apply_goods_issue_invoice_lines(
        self,
        *,
        company_id: str,
        invoice_lines: list[Any],
        stock_product_codes: set[str],
    ) -> list[dict[str, str]]:
        """Reduce stock for posted goods issue using invoice line batch when set — §7.8."""

        issued: list[dict[str, str]] = []
        for line in invoice_lines:
            code = getattr(line, "productCode", None)
            if not code or str(code) not in stock_product_codes:
                continue
            qty = Decimal(str(getattr(line, "quantity", 0)))
            if qty <= 0:
                continue
            batch_number = getattr(line, "batchNumber", None)
            batch = await self._batches.apply_product_delta(
                company_id=company_id,
                product_code=str(code),
                delta=-qty,
                batch_number=str(batch_number) if batch_number else None,
            )
            issued.append(
                {
                    "productCode": str(code),
                    "batchNumber": batch.batchNumber,
                    "quantityIssued": str(qty),
                }
            )
        return issued

    async def apply_grn_receipt_lines(
        self,
        *,
        company_id: str,
        lines: list[Any],
    ) -> list[dict[str, str]]:
        """Add received quantities to product batches on GRN create — P19."""

        applied: list[dict[str, str]] = []
        for line in lines:
            code = getattr(line, "productCode", None)
            if not code:
                continue
            qty = Decimal(str(getattr(line, "quantity", 0)))
            if qty <= 0:
                continue
            batch = await self._batches.apply_product_delta(
                company_id=company_id,
                product_code=str(code),
                delta=qty,
            )
            applied.append(
                {
                    "productCode": str(code),
                    "batchNumber": batch.batchNumber,
                    "quantityReceived": str(qty),
                }
            )
        return applied

    async def apply_delivery_note_lines(
        self,
        *,
        company_id: str,
        lines: list[Any],
    ) -> list[dict[str, str]]:
        """Reduce stock when goods are delivered (GDN) — P21."""

        issued: list[dict[str, str]] = []
        for line in lines:
            code = getattr(line, "productCode", None)
            if not code:
                continue
            qty = Decimal(str(getattr(line, "quantity", 0)))
            if qty <= 0:
                continue
            batch = await self._batches.apply_product_delta(
                company_id=company_id,
                product_code=str(code),
                delta=-qty,
            )
            issued.append(
                {
                    "productCode": str(code),
                    "batchNumber": batch.batchNumber,
                    "quantityIssued": str(qty),
                }
            )
        return issued

    async def restore_delivery_note_lines(
        self,
        *,
        company_id: str,
        lines: list[Any],
    ) -> list[dict[str, str]]:
        """Restore stock when a delivery note is voided — P21."""

        return await self.restore_goods_issue_lines(
            company_id=company_id,
            lines=lines,
        )

    async def reverse_grn_receipt_lines(
        self,
        *,
        company_id: str,
        lines: list[Any],
    ) -> list[dict[str, str]]:
        """Remove quantities previously received on a GRN (void bill path) — P18."""

        rolled_back: list[dict[str, str]] = []
        for line in lines:
            code = getattr(line, "productCode", None)
            if not code:
                continue
            qty = Decimal(str(getattr(line, "quantity", 0)))
            if qty <= 0:
                continue
            batch = await self._batches.apply_product_delta(
                company_id=company_id,
                product_code=str(code),
                delta=-qty,
            )
            rolled_back.append(
                {
                    "productCode": str(code),
                    "batchNumber": batch.batchNumber,
                    "quantityReversed": str(qty),
                }
            )
        return rolled_back
