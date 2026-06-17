"""Budget request bodies."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class BudgetLineInput(BaseModel):
    model_config = {"populate_by_name": True}

    nominal_code: str = Field(..., alias="nominalCode")
    period: str = "annual"
    amount: Decimal = Field(..., gt=0)


class BudgetCreateRequest(BaseModel):
    model_config = {"populate_by_name": True}

    code: str
    name: str
    fiscal_year: int = Field(..., alias="fiscalYear")
    lines: list[BudgetLineInput] = Field(default_factory=list)


class BudgetUpdateRequest(BaseModel):
    model_config = {"populate_by_name": True}

    name: str | None = None
    is_active: bool | None = Field(default=None, alias="isActive")
