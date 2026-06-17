"""Report runner request bodies."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ReportRunRequest(BaseModel):
    """Start a report execution."""

    model_config = {"populate_by_name": True}

    report_id: str = Field(..., alias="reportId")
    criteria: dict[str, Any] = Field(default_factory=dict, alias="criteria")


class ReportExportRequest(BaseModel):
    """Export format for a completed run."""

    model_config = {"populate_by_name": True}

    export_format: Literal["csv", "json", "pdf", "xlsx"] = Field(default="csv", alias="format")


class ReportSyncExportRequest(BaseModel):
    """Execute a catalog report and return export payload in one request."""

    model_config = {"populate_by_name": True}

    report_id: str = Field(..., alias="reportId")
    criteria: dict[str, Any] = Field(default_factory=dict, alias="criteria")
    export_format: Literal["csv", "json", "pdf"] = Field(default="csv", alias="format")
