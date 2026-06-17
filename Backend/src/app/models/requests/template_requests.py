"""Transaction template request bodies — FA §3.3."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TransactionTemplateCreateRequest(BaseModel):
    model_config = {"populate_by_name": True}

    module: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=128)
    payload: dict[str, Any] = Field(default_factory=dict)
