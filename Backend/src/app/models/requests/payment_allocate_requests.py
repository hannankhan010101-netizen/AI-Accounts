"""Allocate an existing supplier payment to open bills."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class PaymentAllocationLineRequest(BaseModel):
    model_config = {"populate_by_name": True}

    bill_id: str = Field(..., alias="billId")
    amount: Decimal = Field(..., gt=0)


class PaymentAllocateRequest(BaseModel):
    model_config = {"populate_by_name": True}

    auto_fifo: bool = Field(default=False, alias="autoFifo")
    allocations: list[PaymentAllocationLineRequest] | None = None
