"""Shared response models (camelCase JSON)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """Liveness payload."""

    model_config = ConfigDict(populate_by_name=True)

    status: str = "ok"


class AuthTokensResponse(BaseModel):
    """OAuth2-style token pair."""

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)

    access_token: str = Field(..., serialization_alias="accessToken")
    refresh_token: str = Field(..., serialization_alias="refreshToken")
    token_type: str = Field(default="bearer", serialization_alias="tokenType")


class MessageResult(BaseModel):
    """Generic envelope with camelCase ``result``."""

    model_config = ConfigDict(populate_by_name=True)

    result: dict | list
