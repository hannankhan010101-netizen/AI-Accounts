"""Lock date request bodies — P4."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class LockDatePerUserRequest(BaseModel):
    model_config = {"populate_by_name": True}

    extended_lock_date: datetime = Field(..., alias="extendedLockDate")
