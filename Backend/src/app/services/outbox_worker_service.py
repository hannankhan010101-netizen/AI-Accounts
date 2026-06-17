"""Process pending outbox events (imports, report runs)."""

from __future__ import annotations

import logging
from typing import Any

from prisma_generated import Prisma

from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.import_job_repository import ImportJobRepository
from app.repositories.outbox_repository import OutboxRepository
from app.repositories.report_run_repository import ReportRunRepository
from app.constants.role_import import ROLE_IMPORT_JOB_TYPE
from app.services.import_handlers import process_import_job
from app.services.clickhouse_export_service import ClickHouseExportService
from app.services.report_query_service import ReportQueryService

logger = logging.getLogger(__name__)

EVENT_IMPORT_JOB = "import_job.process"
EVENT_REPORT_RUN = "report_run.execute"
EVENT_FBR_RETRY = "fbr.submission.retry"
EVENT_CLICKHOUSE_SYNC = "clickhouse.sync.recent"


class OutboxWorkerService:
    def __init__(
        self,
        *,
        outbox_repository: OutboxRepository,
        import_job_repository: ImportJobRepository,
        report_run_repository: ReportRunRepository,
        prisma: Prisma,
        read_prisma: Prisma | None = None,
        audit_log_repository: AuditLogRepository | None = None,
    ) -> None:
        self._outbox = outbox_repository
        self._imports = import_job_repository
        self._report_runs = report_run_repository
        self._audit = audit_log_repository
        self._db = prisma
        report_db = read_prisma or prisma
        self._reports = ReportQueryService(prisma=report_db)
        self._clickhouse = ClickHouseExportService()

    async def process_batch(self, *, limit: int = 20) -> dict[str, int]:
        events = await self._outbox.claim_pending(limit=limit)
        stats = {"processed": 0, "failed": 0}
        for event in events:
            try:
                payload = event.payload if isinstance(event.payload, dict) else {}
                if event.eventType == EVENT_IMPORT_JOB:
                    await self._process_import(
                        company_id=event.companyId, payload=payload
                    )
                elif event.eventType == EVENT_REPORT_RUN:
                    await self._process_report_run(
                        company_id=event.companyId, payload=payload
                    )
                elif event.eventType == EVENT_FBR_RETRY:
                    await self._process_fbr_retry(
                        company_id=event.companyId, payload=payload
                    )
                elif event.eventType == EVENT_CLICKHOUSE_SYNC:
                    await self._process_clickhouse_sync(
                        company_id=event.companyId, payload=payload
                    )
                else:
                    raise ValueError(f"Unknown event type: {event.eventType}")
                await self._outbox.mark_completed(event_id=event.id)
                stats["processed"] += 1
            except Exception as exc:  # noqa: BLE001 — worker must continue
                logger.exception("Outbox event %s failed", event.id)
                await self._outbox.mark_failed(event_id=event.id, error=str(exc))
                stats["failed"] += 1
        return stats

    async def _process_import(
        self, *, company_id: str, payload: dict[str, Any]
    ) -> None:
        job_id = payload.get("importJobId")
        if not job_id:
            raise ValueError("importJobId missing from payload")
        job = await self._imports.get_job(job_id=job_id)
        if job is None or job.companyId != company_id:
            raise ValueError("Import job not found")
        await self._imports.mark_processing(job_id=job_id)
        job_payload = job.payload if isinstance(job.payload, dict) else {}
        rows = job_payload.get("rows") or []
        if not isinstance(rows, list):
            rows = []
        options = {
            k: v for k, v in job_payload.items() if k != "rows"
        }
        result = await process_import_job(
            db=self._db,
            company_id=company_id,
            job_type=job.jobType,
            rows=rows,
            options=options,
        )
        summary = (
            f"created={result.created} posted={result.posted} "
            f"skipped={result.skipped} errors={len(result.errors)}"
        )
        await self._imports.mark_completed(
            job_id=job_id,
            summary=summary,
            error_count=len(result.errors),
        )
        if job.jobType == ROLE_IMPORT_JOB_TYPE and self._audit is not None:
            actor = job_payload.get("requestedByUserId")
            if not isinstance(actor, str):
                actor = None
            await self._audit.append(
                company_id=company_id,
                user_id=actor,
                transaction_type="ROLE_IMPORT_JOB",
                transaction_id=job_id,
                status="completed",
                details=f"file={job.fileName or ''} {summary}",
            )

    async def _process_report_run(
        self, *, company_id: str, payload: dict[str, Any]
    ) -> None:
        run_id = payload.get("reportRunId")
        report_id = payload.get("reportId")
        if not run_id:
            raise ValueError("reportRunId missing from payload")

        run = await self._report_runs.get_run(company_id=company_id, run_id=run_id)
        criteria = run.criteria if run and isinstance(run.criteria, dict) else {}
        rows = await self._reports.execute(
            company_id=company_id,
            report_id=str(report_id or ""),
            criteria=criteria,
        )
        await self._report_runs.complete_run(
            company_id=company_id,
            run_id=run_id,
            rows=rows,
        )
        if self._clickhouse.enabled:
            export = await self._clickhouse.export_report_run(
                company_id=company_id,
                report_id=str(report_id or ""),
                run_id=run_id,
                rows=rows,
            )
            logger.info("ClickHouse export for run %s: %s", run_id, export)

    async def _process_fbr_retry(
        self, *, company_id: str, payload: dict[str, Any]
    ) -> None:
        from app.repositories.fbr_repository import FbrRepository
        from app.repositories.sales_invoice_repository import SalesInvoiceRepository
        from app.services.fbr_service import FbrService

        invoice_id = payload.get("salesInvoiceId")
        if not invoice_id:
            raise ValueError("salesInvoiceId missing from payload")
        service = FbrService(
            fbr_repository=FbrRepository(self._db),
            sales_invoice_repository=SalesInvoiceRepository(self._db),
            outbox_repository=self._outbox,
        )
        await service.process_retry_event(
            company_id=company_id, sales_invoice_id=str(invoice_id)
        )

    async def _process_clickhouse_sync(
        self, *, company_id: str, payload: dict[str, Any]
    ) -> None:
        from app.services.clickhouse_sync_service import ClickHouseSyncService

        days = int(payload.get("days") or 7)
        await ClickHouseSyncService(prisma=self._db).sync_recent_runs(
            company_id=company_id, days=days
        )
