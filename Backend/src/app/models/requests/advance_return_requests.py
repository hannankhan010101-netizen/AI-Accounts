"""Advance return request bodies — FA §5.8 / §6.4."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class AdvanceReturnRequest(BaseModel):
    """Return unallocated advance via bank movement."""

    model_config = {"populate_by_name": True}

    return_date: datetime = Field(..., alias="returnDate")
    amount: Decimal = Field(..., gt=0)
    bank_account_id: str | None = Field(default=None, alias="bankAccountId")
