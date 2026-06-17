"""Report catalog and durable run execution via outbox."""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any, Literal

from app.constants.report_catalog_registry import CATALOG_REPORT_IDS, catalog_coverage
from app.constants.report_module_registry import MODULE_REPORT_IDS
from app.constants.report_definitions import all_report_definitions, favourite_report_ids
from app.core.exceptions import NotFoundError, ValidationAppError
from app.models.responses.report_responses import (
    ReportDefinitionResponse,
    ReportExportResultResponse,
    ReportRunAcceptedResponse,
    ReportRunDetailResponse,
)
from app.repositories.outbox_repository import OutboxRepository
from app.repositories.report_run_repository import ReportRunRepository
from app.services.clickhouse_export_service import ClickHouseExportService
from app.services.outbox_worker_service import EVENT_REPORT_RUN

logger = logging.getLogger(__name__)

ReportHub = Literal["standard", "analytical"]


class ReportService:
    def __init__(
        self,
        *,
        report_run_repository: ReportRunRepository,
        outbox_repository: OutboxRepository,
        clickhouse_export_service: ClickHouseExportService | None = None,
    ) -> None:
        self._runs = report_run_repository
        self._outbox = outbox_repository
        self._clickhouse = clickhouse_export_service or ClickHouseExportService()

    def catalog_coverage_summary(self) -> dict[str, object]:
        return catalog_coverage()

    @staticmethod
    def definitions_etag(
        *,
        category: str | None,
        hub: ReportHub | None,
        favourites_only: bool,
    ) -> str:
        """Stable ETag for report definition list responses."""

        payload = json.dumps(
            {
                "category": category,
                "hub": hub,
                "favouritesOnly": favourites_only,
                "coverage": catalog_coverage(),
            },
            sort_keys=True,
            default=str,
        )
        return hashlib.sha256(payload.encode()).hexdigest()[:32]

    def list_definitions(
        self,
        *,
        category: str | None,
        hub: ReportHub | None,
        favourites_only: bool,
    ) -> list[ReportDefinitionResponse]:
        fav_ids = favourite_report_ids()
        out: list[ReportDefinitionResponse] = []
        for row in all_report_definitions():
            if hub and row.hub != hub:
                continue
            if category and row.category.lower() != category.lower():
                continue
            if favourites_only and row.report_id not in fav_ids:
                continue
            out.append(
                ReportDefinitionResponse(
                    report_id=row.report_id,
                    name=row.name,
                    category=row.category,
                    hub=row.hub,
                    filter_schema=row.filter_schema,
                )
            )
        return sorted(
            out, key=lambda r: (r.hub, r.category, int(r.report_id) if r.report_id.isdigit() else 0)
        )

    async def create_run(
        self,
        *,
        company_id: str,
        report_id: str,
        criteria: dict[str, Any],
    ) -> ReportRunAcceptedResponse:
        valid_ids = (
            {r.report_id for r in all_report_definitions()}
            | set(CATALOG_REPORT_IDS)
            | set(MODULE_REPORT_IDS)
        )
        if report_id not in valid_ids:
            raise NotFoundError(f"Unknown reportId: {report_id}")

        run = await self._runs.create_pending(
            company_id=company_id,
            report_id=report_id,
            criteria=criteria,
        )
        await self._outbox.enqueue(
            company_id=company_id,
            event_type=EVENT_REPORT_RUN,
            payload={"reportRunId": run.id, "reportId": report_id},
        )
        logger.info("Report run %s queued for company %s", run.id, company_id)
        return ReportRunAcceptedResponse(run_id=run.id, status="pending")

    async def complete_run(
        self,
        *,
        company_id: str,
        run_id: str,
        rows: list[dict[str, Any]],
    ) -> None:
        await self._runs.complete_run(
            company_id=company_id,
            run_id=run_id,
            rows=rows,
        )

    async def get_run(self, *, company_id: str, run_id: str) -> ReportRunDetailResponse:
        run = await self._runs.get_run(company_id=company_id, run_id=run_id)
        if run is None:
            raise NotFoundError("Report run not found")
        rows = await self._runs.load_rows_for_run(run)
        return ReportRunDetailResponse(
            run_id=run_id,
            status=run.status,
            report_id=run.reportId,
            total_rows=run.rowCount,
            rows=rows,
        )

    @staticmethod
    def format_rows_export(
        *,
        rows: list[dict[str, Any]],
        export_format: str,
        title: str = "Report",
    ) -> ReportExportResultResponse:
        fmt = export_format.lower()
        if fmt == "xlsx":
            fmt = "csv"
        content: str | None = None
        if fmt == "csv" and rows:
            import csv
            import io

            buf = io.StringIO()
            writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            for row in rows:
                if isinstance(row, dict):
                    writer.writerow(row)
            content = buf.getvalue()
        elif fmt == "json":
            import json

            content = json.dumps(rows, default=str)
        elif fmt == "pdf" and rows:
            import base64

            from app.services.report_pdf_service import rows_to_pdf

            pdf_bytes = rows_to_pdf(title=title, rows=rows)
            content = base64.b64encode(pdf_bytes).decode("ascii")
        return ReportExportResultResponse(
            download_url=None,
            export_format=export_format,
            content=content,
        )

    async def export_run(
        self,
        *,
        company_id: str,
        run_id: str,
        export_format: str,
    ) -> ReportExportResultResponse:
        run = await self._runs.get_run(company_id=company_id, run_id=run_id)
        if run is None:
            raise NotFoundError("Report run not found")
        if run.status != "completed":
            raise ValidationAppError("Run is not ready for export")
        rows = await self._runs.load_rows_for_run(run)
        filtered = [r for r in rows if isinstance(r, dict) and "_meta" not in r]
        return self.format_rows_export(
            rows=filtered,
            export_format=export_format,
            title=f"Report {run.reportId}",
        )

    async def export_run_to_clickhouse(
        self, *, company_id: str, run_id: str
    ) -> dict[str, Any]:
        run = await self._runs.get_run(company_id=company_id, run_id=run_id)
        if run is None:
            raise NotFoundError("Report run not found")
        if run.status != "completed":
            raise ValidationAppError("Run is not ready for ClickHouse export")
        rows = run.rows if isinstance(run.rows, list) else []
        return await self._clickhouse.export_report_run(
            company_id=company_id,
            report_id=run.reportId,
            run_id=run_id,
            rows=rows,
        )
