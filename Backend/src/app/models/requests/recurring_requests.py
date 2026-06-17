"""Recurring schedule API bodies."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class RecurringScheduleCreateRequest(BaseModel):
    model_config = {"populate_by_name": True}

    name: str = Field(..., min_length=1)
    module: str = Field(..., min_length=1)
    frequency: str = Field(default="monthly")
    interval: int = Field(default=1, ge=1)
    next_run_date: datetime = Field(..., alias="nextRunDate")
    end_date: datetime | None = Field(default=None, alias="endDate")
    is_active: bool = Field(default=True, alias="isActive")
    payload: dict[str, Any] = Field(default_factory=dict)


class RecurringScheduleUpdateRequest(BaseModel):
    model_config = {"populate_by_name": True}

    name: str | None = None
    frequency: str | None = None
    interval: int | None = Field(default=None, ge=1)
    next_run_date: datetime | None = Field(default=None, alias="nextRunDate")
    end_date: datetime | None = Field(default=None, alias="endDate")
    is_active: bool | None = Field(default=None, alias="isActive")
    payload: dict[str, Any] | None = None
