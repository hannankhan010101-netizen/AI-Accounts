"""Report runner responses."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ReportDefinitionResponse(BaseModel):
    """Metadata row returned by GET /reports/definitions."""

    model_config = ConfigDict(populate_by_name=True)

    report_id: str = Field(..., serialization_alias="reportId")
    name: str
    category: str
    hub: str
    filter_schema: dict[str, Any] = Field(..., serialization_alias="filterSchema")


class ReportRunAcceptedResponse(BaseModel):
    """Body returned when a run is accepted."""

    model_config = ConfigDict(populate_by_name=True)

    run_id: str = Field(..., serialization_alias="runId")
    status: str


class ReportRunDetailResponse(BaseModel):
    """Paginated run result rows."""

    model_config = ConfigDict(populate_by_name=True)

    run_id: str = Field(..., serialization_alias="runId")
    status: str
    report_id: str = Field(..., serialization_alias="reportId")
    total_rows: int = Field(..., serialization_alias="totalRows")
    rows: list[dict[str, Any]]


class ReportExportResultResponse(BaseModel):
    """Export result — inline content or a download URL."""

    model_config = ConfigDict(populate_by_name=True)

    download_url: str | None = Field(default=None, serialization_alias="downloadUrl")
    export_format: str = Field(..., serialization_alias="format")
    content: str | None = Field(
        default=None,
        description="Inline CSV/JSON payload when download URL is not used",
    )
