"""Bank voucher request bodies."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class BankReceiptCreateRequest(BaseModel):
    """Bank receipt (IR) header (§4.3) with optional counterpart nominal for posting."""

    model_config = {"populate_by_name": True}

    bank_account_id: str = Field(..., alias="bankAccountId")
    receipt_date: datetime = Field(..., alias="receiptDate")
    total_amount: Decimal = Field(..., alias="totalAmount", gt=0)
    nominal_code: str | None = Field(default=None, alias="nominalCode")


class BankTransferCreateRequest(BaseModel):
    """Bank transfer between two accounts (§4.4)."""

    model_config = {"populate_by_name": True}

    from_bank_account_id: str = Field(..., alias="fromBankAccountId")
    to_bank_account_id: str = Field(..., alias="toBankAccountId")
    transfer_date: datetime = Field(..., alias="transferDate")
    total_amount: Decimal = Field(..., alias="totalAmount", gt=0)


class BankPaymentNominalLine(BaseModel):
    model_config = {"populate_by_name": True}

    nominal_code: str = Field(..., alias="nominalCode")
    amount: Decimal = Field(..., gt=0)


class BankPaymentCreateRequest(BaseModel):
    """Bank payment (EP) with single nominal or multi-line split posting."""

    model_config = {"populate_by_name": True}

    bank_account_id: str = Field(..., alias="bankAccountId")
    payment_date: datetime = Field(..., alias="paymentDate")
    total_amount: Decimal = Field(..., alias="totalAmount", gt=0)
    nominal_code: str | None = Field(default=None, alias="nominalCode")
    nominal_lines: list[BankPaymentNominalLine] | None = Field(
        default=None, alias="nominalLines"
    )
    smart_filters: dict[str, str] | None = Field(default=None, alias="smartFilters")
