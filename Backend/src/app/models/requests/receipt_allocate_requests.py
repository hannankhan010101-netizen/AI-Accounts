"""Allocate an existing sales receipt to open invoices — P9."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class ReceiptAllocationLineRequest(BaseModel):
    model_config = {"populate_by_name": True}

    invoice_id: str = Field(..., alias="invoiceId")
    amount: Decimal = Field(..., gt=0)


class ReceiptAllocateRequest(BaseModel):
    model_config = {"populate_by_name": True}

    auto_fifo: bool = Field(default=False, alias="autoFifo")
    allocations: list[ReceiptAllocationLineRequest] | None = None
