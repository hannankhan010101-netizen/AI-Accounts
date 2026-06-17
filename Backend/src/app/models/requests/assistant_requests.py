"""Assistant API request bodies."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AssistantChatStreamRequest(BaseModel):
    message: str = Field(..., max_length=8000)
    pathname: str = Field(default="/", max_length=500)
    thread_id: str | None = Field(default=None, alias="threadId")
    locale: str | None = Field(default="en", max_length=16)
    mode: str | None = Field(default=None, max_length=32)
    entity_context: dict[str, Any] | None = Field(default=None, alias="entityContext")

    model_config = {"populate_by_name": True}


class AssistantToolResultRequest(BaseModel):
    thread_id: str = Field(..., alias="threadId")
    tool_call_id: str = Field(..., alias="toolCallId")
    result: dict[str, Any] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}
