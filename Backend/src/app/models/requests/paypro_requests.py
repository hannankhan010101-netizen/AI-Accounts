"""PayPro / Kuickpay request bodies — P5/P9."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class PaymentAllocationLineRequest(BaseModel):
    model_config = {"populate_by_name": True}

    invoice_id: str = Field(..., alias="invoiceId")
    amount: Decimal = Field(..., gt=0)


class PayproInitiateRequest(BaseModel):
    model_config = {"populate_by_name": True}

    customer_id: str = Field(..., alias="customerId")
    amount: Decimal = Field(..., gt=0)
    bank_account_id: str | None = Field(default=None, alias="bankAccountId")


class PayproWebhookRequest(BaseModel):
    model_config = {"populate_by_name": True}

    merchant_ref: str = Field(..., alias="merchantRef")
    status: str = "settled"
    sales_receipt_id: str | None = Field(default=None, alias="salesReceiptId")
    auto_fifo: bool = Field(default=True, alias="autoFifo")
    allocations: list[PaymentAllocationLineRequest] | None = None
