"""Master-data request bodies — catalog §5.1, §6.1, §7.1, §4.1."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field, field_validator


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


class OpeningStockInput(BaseModel):
    """Optional opening quantity when creating a stock product."""

    model_config = {"populate_by_name": True}

    quantity: float = Field(..., gt=0)
    rate: float | None = Field(default=None, ge=0)


class CreateProductRequest(BaseModel):
    """Create a product (§7.1 product master)."""

    model_config = {"populate_by_name": True}

    code: str | None = Field(default=None, max_length=32)
    name: str = Field(..., min_length=1, max_length=200)
    is_stock: bool = Field(default=True, alias="isStock")
    unit: str = Field(default="EA", max_length=16)
    category: str | None = Field(default=None, max_length=64)
    cost: float | None = Field(default=None, ge=0)
    sale_price: float | None = Field(default=None, ge=0, alias="salePrice")
    low_stock_level: float | None = Field(default=None, ge=0, alias="lowStockLevel")
    bin_location: str | None = Field(default=None, max_length=64, alias="binLocation")
    opening_stock: OpeningStockInput | None = Field(default=None, alias="openingStock")

    @field_validator("unit")
    @classmethod
    def normalize_unit(cls, v: str) -> str:
        cleaned = (v or "EA").strip().upper()
        return cleaned[:16] if cleaned else "EA"


class UpdateProductRequest(BaseModel):
    """Update product master fields."""

    model_config = {"populate_by_name": True}

    name: str = Field(..., min_length=1, max_length=200)
    is_stock: bool = Field(alias="isStock")
    unit: str = Field(default="EA", max_length=16)
    category: str | None = Field(default=None, max_length=64)
    cost: float | None = Field(default=None, ge=0)
    sale_price: float | None = Field(default=None, ge=0, alias="salePrice")
    low_stock_level: float | None = Field(default=None, ge=0, alias="lowStockLevel")
    bin_location: str | None = Field(default=None, max_length=64, alias="binLocation")
    custom_fields: dict | None = Field(default=None, alias="customFields")

    @field_validator("unit")
    @classmethod
    def normalize_unit(cls, v: str) -> str:
        cleaned = (v or "EA").strip().upper()
        return cleaned[:16] if cleaned else "EA"


class SetPrimaryImageRequest(BaseModel):
    model_config = {"populate_by_name": True}

    attachment_id: str | None = Field(default=None, alias="attachmentId")


class OpeningStockRequest(BaseModel):
    model_config = {"populate_by_name": True}

    quantity: float = Field(..., gt=0)
    rate: float | None = Field(default=None, ge=0)


class CreateBankAccountRequest(BaseModel):
    """Create a bank or cash account (§4.1)."""

    model_config = {"populate_by_name": True}

    name: str = Field(..., min_length=1, max_length=200)
    nominal_code: str | None = Field(default=None, alias="nominalCode", max_length=32)
    currency: str = Field(default="PKR", min_length=3, max_length=3)
