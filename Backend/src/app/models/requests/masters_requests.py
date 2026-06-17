"""Master-data request bodies — catalog §5.1, §6.1, §7.1, §4.1."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class CreateCustomerRequest(BaseModel):
    """Create a customer (§5.1)."""

    model_config = {"populate_by_name": True}

    code: str | None = Field(default=None, max_length=32)
    name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=32)


class CreateSupplierRequest(BaseModel):
    """Create a supplier (§6.1)."""

    model_config = {"populate_by_name": True}

    code: str | None = Field(default=None, max_length=32)
    name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=32)


class CreateProductRequest(BaseModel):
    """Create a product (§7.1 — minimal master, pricing fields land in Phase 6)."""

    model_config = {"populate_by_name": True}

    code: str | None = Field(default=None, max_length=32)
    name: str = Field(..., min_length=1, max_length=200)
    is_stock: bool = Field(default=True, alias="isStock")


class CreateBankAccountRequest(BaseModel):
    """Create a bank or cash account (§4.1)."""

    model_config = {"populate_by_name": True}

    name: str = Field(..., min_length=1, max_length=200)
    nominal_code: str | None = Field(default=None, alias="nominalCode", max_length=32)
    currency: str = Field(default="PKR", min_length=3, max_length=3)
