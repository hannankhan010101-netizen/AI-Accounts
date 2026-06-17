"""FX revaluation request bodies — P4."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class FxRevaluationRequest(BaseModel):
    model_config = {"populate_by_name": True}

    bank_account_id: str = Field(..., alias="bankAccountId")
    revaluation_date: datetime = Field(..., alias="revaluationDate")
    foreign_balance: Decimal = Field(..., alias="foreignBalance")
    exchange_rate: Decimal = Field(..., gt=0, alias="exchangeRate")
    book_balance_base: Decimal | None = Field(default=None, alias="bookBalanceBase")
