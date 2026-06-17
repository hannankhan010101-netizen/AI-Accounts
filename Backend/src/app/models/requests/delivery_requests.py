"""Delivery / GRN request bodies — Sprint 12."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class DeliveryLineRequest(BaseModel):
    """One line on a delivery / GRN."""

    model_config = {"populate_by_name": True}

    product_code: str | None = Field(default=None, alias="productCode")
    quantity: Decimal = Field(..., gt=0)
    notes: str | None = None


class DeliveryNoteCreateRequest(BaseModel):
    """§5.6 — GDNSI from invoice, GDNSO from sales order, or manual."""

    model_config = {"populate_by_name": True}

    delivery_date: datetime = Field(..., alias="deliveryDate")
    customer_id: str = Field(..., alias="customerId")
    source_kind: Literal["GDNSI", "GDNSO", "manual"] = Field(..., alias="sourceKind")
    source_id: str | None = Field(default=None, alias="sourceId")
    notes: str | None = None
    lines: list[DeliveryLineRequest] = Field(..., min_length=1)
    skip_stock_movement: bool = Field(
        default=False,
        alias="skipStockMovement",
        description="When true, do not reduce batch quantities (P22).",
    )

    def to_repo_lines(self) -> list[dict]:
        return [
            {"productCode": l.product_code, "quantity": l.quantity, "notes": l.notes}
            for l in self.lines
        ]


class GoodsReceiptNoteCreateRequest(BaseModel):
    """§6 — GRNPO from PO, GRNVI from bill, or manual."""

    model_config = {"populate_by_name": True}

    receipt_date: datetime = Field(..., alias="receiptDate")
    supplier_id: str = Field(..., alias="supplierId")
    source_kind: Literal["GRNPO", "GRNVI", "manual"] = Field(..., alias="sourceKind")
    source_id: str | None = Field(default=None, alias="sourceId")
    notes: str | None = None
    lines: list[DeliveryLineRequest] = Field(..., min_length=1)
    skip_stock_movement: bool = Field(
        default=False,
        alias="skipStockMovement",
        description="When true, do not increase batch quantities (P23).",
    )

    def to_repo_lines(self) -> list[dict]:
        return [
            {"productCode": l.product_code, "quantity": l.quantity, "notes": l.notes}
            for l in self.lines
        ]
