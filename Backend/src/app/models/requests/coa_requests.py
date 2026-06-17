"""Chart of Account request bodies — catalog §9.1."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


CategoryType = Literal["Income", "Expense", "Asset", "Liability", "Equity", "Other"]


class CreateSectionRequest(BaseModel):
    """Create a section under a category (§9.1.4)."""

    model_config = {"populate_by_name": True}

    category_id: str = Field(..., alias="categoryId")
    code: str = Field(..., min_length=1, max_length=32)
    name: str = Field(..., min_length=1, max_length=128)


class ReorderSectionRequest(BaseModel):
    """Move a section up or down within its category (§9.1.4)."""

    model_config = {"populate_by_name": True}

    direction: Literal["up", "down"]


class UpdateCategoryTypeRequest(BaseModel):
    """Set the P&L/BS classification on a category (§9.1.1)."""

    model_config = {"populate_by_name": True}

    category_type: CategoryType = Field(..., alias="categoryType")


class CreateNominalRequest(BaseModel):
    """Create a nominal account under a section (§9.1.2)."""

    model_config = {"populate_by_name": True}

    section_id: str = Field(..., alias="sectionId")
    code: str | None = Field(default=None, min_length=1, max_length=32)
    name: str = Field(..., min_length=1, max_length=128)
    description: str | None = None
    is_charge_deduction: bool = Field(default=False, alias="isChargeDeduction")


class UpdateNominalRequest(BaseModel):
    """Edit nominal metadata (§9.1.2). Code is immutable after create."""

    model_config = {"populate_by_name": True}

    name: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = None
    is_charge_deduction: bool | None = Field(default=None, alias="isChargeDeduction")


class MoveNominalRequest(BaseModel):
    """Move a nominal to another section within the same company chart."""

    model_config = {"populate_by_name": True}

    section_id: str = Field(..., alias="sectionId")
