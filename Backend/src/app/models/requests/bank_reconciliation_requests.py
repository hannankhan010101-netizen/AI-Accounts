"""Bank reconciliation API bodies."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class BankReconciliationStartRequest(BaseModel):
    model_config = {"populate_by_name": True}

    bank_account_id: str = Field(..., alias="bankAccountId")
    statement_date: datetime = Field(..., alias="statementDate")
    statement_balance: Decimal = Field(..., alias="statementBalance")
    notes: str | None = None


class BankReconciliationClearRequest(BaseModel):
    model_config = {"populate_by_name": True}

    item_ids: list[str] = Field(..., alias="itemIds", min_length=1)
    cleared: bool = True


class JournalReverseRequest(BaseModel):
    model_config = {"populate_by_name": True}

    reversal_date: datetime = Field(..., alias="reversalDate")
    ref_no: str | None = Field(default=None, alias="refNo")
