"""Platform / cross-cutting request bodies."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ReserveDocumentNumberRequest(BaseModel):
    """Reserve the next number for a logical sequence."""

    model_config = {"populate_by_name": True}

    sequence_key: str = Field(..., min_length=1, alias="sequenceKey")


class CreateAttachmentRequest(BaseModel):
    """Register uploaded attachment metadata."""

    model_config = {"populate_by_name": True}

    entity_type: str = Field(..., alias="entityType")
    entity_id: str = Field(..., alias="entityId")
    file_name: str = Field(..., alias="fileName")
    storage_key: str = Field(..., alias="storageKey")
    mime_type: str | None = Field(default=None, alias="mimeType")
    byte_size: int = Field(..., ge=0, alias="byteSize")


class CreateImportJobRequest(BaseModel):
    """Create a bulk import job."""

    model_config = {"populate_by_name": True}

    job_type: str = Field(..., alias="jobType")
    file_name: str | None = Field(default=None, alias="fileName")
    rows: list[dict] = Field(default_factory=list)
    post_gl: bool = Field(default=False, alias="postGl")


class UpsertApprovalPolicyRequest(BaseModel):
    """Replace rules JSON for an entity type."""

    model_config = {"populate_by_name": True}

    entity_type: str = Field(..., alias="entityType")
    rules: dict = Field(default_factory=dict, alias="rules")
