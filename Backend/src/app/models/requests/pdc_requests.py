"""Post-Dated Cheque request bodies — Sprint 14, catalog §5.7 / §6.1."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class PdcReceivedCreateRequest(BaseModel):
    """Post-dated cheque received from a customer (§5.7)."""

    model_config = {"populate_by_name": True}

    cheque_number: str = Field(..., alias="chequeNumber")
    bank_name: str = Field(..., alias="bankName")
    customer_id: str = Field(..., alias="customerId")
    received_date: datetime = Field(..., alias="receivedDate")
    cheque_date: datetime = Field(..., alias="chequeDate")
    amount: Decimal = Field(..., gt=0)
    notes: str | None = None


class PdcIssuedCreateRequest(BaseModel):
    """Post-dated cheque issued to a supplier (§6.1)."""

    model_config = {"populate_by_name": True}

    cheque_number: str = Field(..., alias="chequeNumber")
    bank_account_id: str = Field(..., alias="bankAccountId")
    supplier_id: str = Field(..., alias="supplierId")
    issued_date: datetime = Field(..., alias="issuedDate")
    cheque_date: datetime = Field(..., alias="chequeDate")
    amount: Decimal = Field(..., gt=0)
    notes: str | None = None


class PdcStatusUpdateRequest(BaseModel):
    """Move a PDC through the lifecycle: pending → presented → cleared/bounced/cancelled."""

    model_config = {"populate_by_name": True}

    status: Literal["pending", "presented", "cleared", "bounced", "cancelled"]


class PdcClearReceivedRequest(BaseModel):
    """Clear a received PDC into a bank receipt and GL."""

    model_config = {"populate_by_name": True}

    bank_account_id: str = Field(..., alias="bankAccountId")
    clear_date: datetime = Field(..., alias="clearDate")
    auto_fifo: bool = Field(default=True, alias="autoFifo")


class PdcClearIssuedRequest(BaseModel):
    """Clear an issued PDC into a supplier payment and GL."""

    model_config = {"populate_by_name": True}

    clear_date: datetime = Field(..., alias="clearDate")
    auto_fifo: bool = Field(default=True, alias="autoFifo")
