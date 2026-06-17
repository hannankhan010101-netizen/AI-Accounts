"""Inventory write request bodies — Sprint 8 (catalog §7.2 / §7.3 / §7.8)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class StockAdjustmentLineRequest(BaseModel):
    """One line on a stock adjustment."""

    model_config = {"populate_by_name": True}

    product_code: str = Field(..., alias="productCode", min_length=1)
    location_code: str | None = Field(default=None, alias="locationCode")
    quantity_delta: Decimal = Field(..., alias="quantityDelta")
    unit_cost: Decimal = Field(default=Decimal(0), alias="unitCost")


class StockAdjustmentCreateRequest(BaseModel):
    """§7.3 stock adjustment voucher."""

    model_config = {"populate_by_name": True}

    adjustment_date: datetime = Field(..., alias="adjustmentDate")
    reason: str = Field(default="adjustment")
    notes: str | None = None
    lines: list[StockAdjustmentLineRequest] = Field(..., min_length=1)

    def to_repo_lines(self) -> list[dict]:
        return [
            {
                "productCode": l.product_code,
                "locationCode": l.location_code,
                "quantityDelta": l.quantity_delta,
                "unitCost": l.unit_cost,
            }
            for l in self.lines
        ]


class StockTransferLineRequest(BaseModel):
    """One line on a stock transfer."""

    model_config = {"populate_by_name": True}

    product_code: str = Field(..., alias="productCode", min_length=1)
    quantity: Decimal = Field(..., gt=0)
    unit_cost: Decimal = Field(default=Decimal(0), alias="unitCost")


class StockTransferCreateRequest(BaseModel):
    """§7.2 stock transfer between two locations."""

    model_config = {"populate_by_name": True}

    transfer_date: datetime = Field(..., alias="transferDate")
    from_location_code: str = Field(..., alias="fromLocationCode")
    to_location_code: str = Field(..., alias="toLocationCode")
    notes: str | None = None
    lines: list[StockTransferLineRequest] = Field(..., min_length=1)

    def to_repo_lines(self) -> list[dict]:
        return [
            {
                "productCode": l.product_code,
                "quantity": l.quantity,
                "unitCost": l.unit_cost,
            }
            for l in self.lines
        ]


class ProductBatchCreateRequest(BaseModel):
    """§7.8 product batch + expiry tracking."""

    model_config = {"populate_by_name": True}

    product_code: str = Field(..., alias="productCode", min_length=1)
    batch_number: str = Field(..., alias="batchNumber", min_length=1)
    expiry_date: datetime | None = Field(default=None, alias="expiryDate")
    quantity_on_hand: Decimal = Field(default=Decimal(0), alias="quantityOnHand")
    notes: str | None = None
