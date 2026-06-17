"""Import job lifecycle (queue only in this slice)."""

from __future__ import annotations

from app.repositories.import_job_repository import ImportJobRepository
from app.repositories.outbox_repository import OutboxRepository
from app.services.import_excel_service import parse_upload
from app.constants.role_import import ROLE_IMPORT_JOB_TYPE
from app.services.outbox_worker_service import EVENT_IMPORT_JOB
from app.services.role_import_parser import parse_role_import_file


class ImportJobService:
    """Create and list background import jobs."""

    def __init__(
        self,
        *,
        import_job_repository: ImportJobRepository,
        outbox_repository: OutboxRepository | None = None,
    ) -> None:
        self._repo = import_job_repository
        self._outbox = outbox_repository

    async def list_jobs(self, *, company_id: str):
        """Return recent jobs."""

        return await self._repo.list_for_company(company_id=company_id)

    async def get_job(self, *, company_id: str, job_id: str):
        """Return job when it belongs to the company."""

        job = await self._repo.get_job(job_id=job_id)
        if job is None or job.companyId != company_id:
            return None
        return job

    async def enqueue(
        self,
        *,
        company_id: str,
        job_type: str,
        file_name: str | None,
        rows: list[dict] | None = None,
        extra_payload: dict | None = None,
    ):
        """Insert a pending job row."""

        payload: dict = dict(extra_payload or {})
        if rows:
            payload["rows"] = rows
        job = await self._repo.create_pending(
            company_id=company_id,
            job_type=job_type,
            file_name=file_name,
            payload=payload,
        )
        if self._outbox is not None:
            await self._outbox.enqueue(
                company_id=company_id,
                event_type=EVENT_IMPORT_JOB,
                payload={"importJobId": job.id},
            )
        return job

    async def enqueue_from_file(
        self,
        *,
        company_id: str,
        job_type: str,
        filename: str,
        content: bytes,
        post_gl: bool = False,
    ):
        rows = parse_upload(filename=filename, content=content)
        extra: dict = {"postGl": True} if post_gl else {}
        return await self.enqueue(
            company_id=company_id,
            job_type=job_type,
            file_name=filename,
            rows=rows,
            extra_payload=extra or None,
        )

    async def enqueue_role_import_file(
        self,
        *,
        company_id: str,
        filename: str,
        content: bytes,
        skip_existing: bool = True,
        requested_by_user_id: str | None = None,
    ):
        """Parse roles file and queue background import — P33."""

        entries = parse_role_import_file(filename=filename, content=content)
        extra: dict = {"skipExisting": skip_existing}
        if requested_by_user_id:
            extra["requestedByUserId"] = requested_by_user_id
        return await self.enqueue(
            company_id=company_id,
            job_type=ROLE_IMPORT_JOB_TYPE,
            file_name=filename,
            rows=entries,
            extra_payload=extra,
        )
