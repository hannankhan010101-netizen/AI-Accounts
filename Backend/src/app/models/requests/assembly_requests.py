"""Assembly request bodies — P4."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class AssemblyTemplateLineInput(BaseModel):
    model_config = {"populate_by_name": True}

    component_product_code: str = Field(..., alias="componentProductCode")
    quantity: Decimal = Field(..., gt=0)


class AssemblyTemplateCreateRequest(BaseModel):
    model_config = {"populate_by_name": True}

    code: str
    name: str
    finished_product_code: str = Field(..., alias="finishedProductCode")
    lines: list[AssemblyTemplateLineInput]


class AssemblyJobCreateRequest(BaseModel):
    model_config = {"populate_by_name": True}

    template_id: str = Field(..., alias="templateId")
    job_date: datetime = Field(..., alias="jobDate")
    quantity: Decimal = Field(..., gt=0)
    batch_number: str | None = Field(default=None, alias="batchNumber")
    expiry_date: datetime | None = Field(default=None, alias="expiryDate")
