"""Sales document request bodies — catalog §5."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class SalesInvoiceLineRequest(BaseModel):
    """One line on a sales invoice."""

    model_config = {"populate_by_name": True}

    product_code: str | None = Field(default=None, alias="productCode")
    quantity: Decimal = Field(..., gt=0)
    rate: Decimal = Field(..., ge=0)
    gst_code: str | None = Field(default=None, alias="gstCode")
    gst_rate: Decimal | None = Field(default=None, ge=0, alias="gstRate")
    adt_code: str | None = Field(default=None, alias="adtCode")
    fed_code: str | None = Field(default=None, alias="fedCode")
    project_code: str | None = Field(default=None, alias="projectCode")
    description: str | None = None
    description_fields: dict[str, str] | None = Field(default=None, alias="descriptionFields")
    batch_number: str | None = Field(default=None, alias="batchNumber")
    expiry_date: datetime | None = Field(default=None, alias="expiryDate")


class SimpleLineRequest(BaseModel):
    """Line shape shared by quotation / sales order / sales credit (no project)."""

    model_config = {"populate_by_name": True}

    product_code: str | None = Field(default=None, alias="productCode")
    quantity: Decimal = Field(..., gt=0)
    rate: Decimal = Field(..., ge=0)
    gst_code: str | None = Field(default=None, alias="gstCode")
    gst_rate: Decimal | None = Field(default=None, ge=0, alias="gstRate")

    def to_raw_line(self) -> dict[str, Any]:
        return {
            "productCode": self.product_code,
            "quantity": self.quantity,
            "rate": self.rate,
            "gstCode": self.gst_code,
            "gstRate": self.gst_rate,
        }

    def to_repo(self) -> dict[str, Any]:
        """Net-only line for documents without GST columns (e.g. sales credit)."""

        return {
            "productCode": self.product_code,
            "quantity": self.quantity,
            "rate": self.rate,
            "lineTotal": self.quantity * self.rate,
        }


class QuotationCreateRequest(BaseModel):
    """Quotation (SQ) — catalog §5.2."""

    model_config = {"populate_by_name": True}

    quotation_date: datetime = Field(..., alias="quotationDate")
    customer_id: str = Field(..., alias="customerId")
    lines: list[SimpleLineRequest] = Field(..., min_length=1)

    def to_raw_lines(self) -> list[dict[str, Any]]:
        return [line.to_raw_line() for line in self.lines]


class SalesOrderCreateRequest(BaseModel):
    """Sales order — catalog §5.3. Status transitions via PUT."""

    model_config = {"populate_by_name": True}

    order_date: datetime = Field(..., alias="orderDate")
    customer_id: str = Field(..., alias="customerId")
    lines: list[SimpleLineRequest] = Field(..., min_length=1)

    def to_raw_lines(self) -> list[dict[str, Any]]:
        return [line.to_raw_line() for line in self.lines]


class SalesCreditCreateRequest(BaseModel):
    """Sales credit (SC) — catalog §5.5."""

    model_config = {"populate_by_name": True}

    credit_date: datetime = Field(..., alias="creditDate")
    customer_id: str = Field(..., alias="customerId")
    lines: list[SimpleLineRequest] = Field(..., min_length=1)

    def to_raw_lines(self) -> list[dict[str, Any]]:
        return [line.to_raw_line() for line in self.lines]


class StatusTransitionRequest(BaseModel):
    """Set the status on a quotation / sales order / purchase order."""

    model_config = {"populate_by_name": True}

    status: str


class ReceiptAllocationLineRequest(BaseModel):
    """One explicit allocation row against an invoice."""

    model_config = {"populate_by_name": True}

    invoice_id: str = Field(..., alias="invoiceId")
    amount: Decimal = Field(..., gt=0)


class SalesReceiptCreateRequest(BaseModel):
    """Customer receipt (§5.8). FIFO auto-allocation when ``autoFifo`` is true,
    or pass ``allocations`` to clear specific invoices."""

    model_config = {"populate_by_name": True}

    receipt_date: datetime = Field(..., alias="receiptDate")
    customer_id: str = Field(..., alias="customerId")
    bank_account_id: str = Field(..., alias="bankAccountId")
    total_amount: Decimal = Field(..., alias="totalAmount", gt=0)
    auto_fifo: bool = Field(default=False, alias="autoFifo")
    allocations: list[ReceiptAllocationLineRequest] | None = None
    wht_code: str | None = Field(default=None, alias="whtCode")
    wht_amount: Decimal | None = Field(default=None, ge=0, alias="whtAmount")
    payment_method: str | None = Field(default=None, alias="paymentMethod")
    smart_filters: dict[str, str] | None = Field(default=None, alias="smartFilters")


class SalesInvoiceCreateRequest(BaseModel):
    """Create a sales invoice (§5.4 — minimal slice, taxes + discounts in 4.4 follow-up)."""

    model_config = {"populate_by_name": True}

    invoice_date: datetime = Field(..., alias="invoiceDate")
    customer_id: str = Field(..., alias="customerId")
    lines: list[SalesInvoiceLineRequest] = Field(..., min_length=1)
    smart_filters: dict[str, str] | None = Field(default=None, alias="smartFilters")

    def to_raw_lines(self) -> list[dict[str, Any]]:
        """Raw lines for tax service (taxes computed server-side)."""

        out: list[dict[str, Any]] = []
        for line in self.lines:
            row: dict[str, Any] = {
                "productCode": line.product_code,
                "quantity": line.quantity,
                "rate": line.rate,
                "projectCode": line.project_code,
            }
            if line.gst_code:
                row["gstCode"] = line.gst_code
            if line.gst_rate is not None:
                row["gstRate"] = line.gst_rate
            if line.adt_code:
                row["adtCode"] = line.adt_code
            if line.fed_code:
                row["fedCode"] = line.fed_code
            if line.description:
                row["description"] = line.description
            if line.description_fields:
                row["descriptionFields"] = line.description_fields
            if line.batch_number:
                row["batchNumber"] = line.batch_number
            if line.expiry_date is not None:
                row["expiryDate"] = line.expiry_date
            out.append(row)
        return out


class BatchSalesInvoiceEntryRequest(SalesInvoiceLineRequest):
    """One batch grid row — party + line."""

    customer_id: str = Field(..., alias="customerId")


class BatchSalesInvoiceCreateRequest(BaseModel):
    """Batch sales invoice entry — groups rows by customer (§3.9)."""

    model_config = {"populate_by_name": True}

    invoice_date: datetime = Field(..., alias="invoiceDate")
    entries: list[BatchSalesInvoiceEntryRequest] = Field(..., min_length=1)


class SalesInvoiceEmailRequest(BaseModel):
    """Optional override recipient for invoice email."""

    to: str | None = Field(default=None, min_length=3, max_length=254)
    smart_filters: dict[str, str] | None = Field(default=None, alias="smartFilters")
