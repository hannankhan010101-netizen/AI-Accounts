"""Purchase document request bodies — catalog §6."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class SupplierBillLineRequest(BaseModel):
    """One line on a supplier bill."""

    model_config = {"populate_by_name": True}

    product_code: str | None = Field(default=None, alias="productCode")
    quantity: Decimal = Field(..., gt=0)
    rate: Decimal = Field(..., ge=0)
    gst_code: str | None = Field(default=None, alias="gstCode")
    gst_rate: Decimal | None = Field(default=None, ge=0, alias="gstRate")
    adt_code: str | None = Field(default=None, alias="adtCode")
    fed_code: str | None = Field(default=None, alias="fedCode")
    description: str | None = None
    description_fields: dict[str, str] | None = Field(default=None, alias="descriptionFields")
    batch_number: str | None = Field(default=None, alias="batchNumber")
    expiry_date: datetime | None = Field(default=None, alias="expiryDate")


class SimplePurchaseLineRequest(BaseModel):
    """Line shape shared by purchase order / supplier credit."""

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
        """Net-only line for documents without GST columns (e.g. supplier credit)."""

        return {
            "productCode": self.product_code,
            "quantity": self.quantity,
            "rate": self.rate,
            "lineTotal": self.quantity * self.rate,
        }


class PurchaseOrderCreateRequest(BaseModel):
    """Purchase order — catalog §6.2."""

    model_config = {"populate_by_name": True}

    order_date: datetime = Field(..., alias="orderDate")
    supplier_id: str = Field(..., alias="supplierId")
    lines: list[SimplePurchaseLineRequest] = Field(..., min_length=1)

    def to_raw_lines(self) -> list[dict[str, Any]]:
        return [l.to_raw_line() for l in self.lines]


class SupplierCreditCreateRequest(BaseModel):
    """Supplier credit (VC) — catalog §6.3."""

    model_config = {"populate_by_name": True}

    credit_date: datetime = Field(..., alias="creditDate")
    supplier_id: str = Field(..., alias="supplierId")
    lines: list[SimplePurchaseLineRequest] = Field(..., min_length=1)

    def to_raw_lines(self) -> list[dict[str, Any]]:
        return [line.to_raw_line() for line in self.lines]


class PaymentAllocationLineRequest(BaseModel):
    """One explicit allocation row against a bill."""

    model_config = {"populate_by_name": True}

    bill_id: str = Field(..., alias="billId")
    amount: Decimal = Field(..., gt=0)


class SupplierPaymentCreateRequest(BaseModel):
    """Supplier payment (§6.4). FIFO auto-allocation when ``autoFifo`` is true,
    or pass ``allocations`` to clear specific bills."""

    model_config = {"populate_by_name": True}

    payment_date: datetime = Field(..., alias="paymentDate")
    supplier_id: str = Field(..., alias="supplierId")
    bank_account_id: str = Field(..., alias="bankAccountId")
    total_amount: Decimal = Field(..., alias="totalAmount", gt=0)
    auto_fifo: bool = Field(default=False, alias="autoFifo")
    allocations: list[PaymentAllocationLineRequest] | None = None
    wht_code: str | None = Field(default=None, alias="whtCode")
    wht_amount: Decimal | None = Field(default=None, ge=0, alias="whtAmount")
    payment_method: str | None = Field(default=None, alias="paymentMethod")
    smart_filters: dict[str, str] | None = Field(default=None, alias="smartFilters")


class SupplierBillCreateRequest(BaseModel):
    """Create a supplier bill (§6.3 minimal — taxes / WHT / additional charges land in Phase 5.3)."""

    model_config = {"populate_by_name": True}

    bill_date: datetime = Field(..., alias="billDate")
    supplier_id: str = Field(..., alias="supplierId")
    lines: list[SupplierBillLineRequest] = Field(..., min_length=1)
    smart_filters: dict[str, str] | None = Field(default=None, alias="smartFilters")

    def to_raw_lines(self) -> list[dict[str, Any]]:
        """Raw lines for tax service (taxes computed server-side)."""

        out: list[dict[str, Any]] = []
        for line in self.lines:
            row: dict[str, Any] = {
                "productCode": line.product_code,
                "quantity": line.quantity,
                "rate": line.rate,
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


class BatchSupplierBillEntryRequest(SupplierBillLineRequest):
    """One batch grid row — party + line."""

    supplier_id: str = Field(..., alias="supplierId")


class BatchSupplierBillCreateRequest(BaseModel):
    """Batch supplier bill entry — groups rows by supplier (§3.9)."""

    model_config = {"populate_by_name": True}

    bill_date: datetime = Field(..., alias="billDate")
    entries: list[BatchSupplierBillEntryRequest] = Field(..., min_length=1)
    smart_filters: dict[str, str] | None = Field(default=None, alias="smartFilters")
