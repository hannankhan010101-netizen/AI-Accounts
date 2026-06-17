"""Project and location request bodies."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CreateProjectRequest(BaseModel):
    model_config = {"populate_by_name": True}

    code: str
    name: str


class UpdateProjectRequest(BaseModel):
    model_config = {"populate_by_name": True}

    name: str | None = None
    is_active: bool | None = Field(default=None, alias="isActive")


class CreateLocationRequest(BaseModel):
    model_config = {"populate_by_name": True}

    code: str
    name: str
    is_main: bool = Field(default=False, alias="isMain")


class UpdateLocationRequest(BaseModel):
    model_config = {"populate_by_name": True}

    name: str | None = None
    is_main: bool | None = Field(default=None, alias="isMain")
