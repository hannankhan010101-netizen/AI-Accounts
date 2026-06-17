"""Approval request bodies — P3."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class ApprovalRequestCreate(BaseModel):
    model_config = {"populate_by_name": True}

    entity_type: str = Field(..., alias="entityType")
    entity_id: str = Field(..., alias="entityId")
    amount: Decimal = Field(..., gt=0)
    notes: str | None = None
