"""Bulk import job persistence."""

from __future__ import annotations

from prisma_generated import Prisma
from prisma_generated.models import ImportJob


class ImportJobRepository:
    """Track long-running Excel / CSV import pipelines."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_for_company(self, *, company_id: str, take: int = 50) -> list[ImportJob]:
        """Return recent jobs newest first."""

        return await self._db.importjob.find_many(
            where={"companyId": company_id},
            order={"createdAt": "desc"},
            take=take,
        )

    async def get_job(self, *, job_id: str) -> ImportJob | None:
        return await self._db.importjob.find_unique(where={"id": job_id})

    async def create_pending(
        self,
        *,
        company_id: str,
        job_type: str,
        file_name: str | None,
        payload: dict | None = None,
    ) -> ImportJob:
        """Insert a job in ``pending`` status."""

        return await self._db.importjob.create(
            data={
                "companyId": company_id,
                "jobType": job_type,
                "status": "pending",
                "fileName": file_name,
                "payload": payload or {},
            }
        )

    async def mark_processing(self, *, job_id: str) -> None:
        await self._db.importjob.update(
            where={"id": job_id},
            data={"status": "processing"},
        )

    async def mark_completed(
        self, *, job_id: str, summary: str, error_count: int = 0
    ) -> None:
        await self._db.importjob.update(
            where={"id": job_id},
            data={
                "status": "completed",
                "resultSummary": summary,
                "errorCount": error_count,
            },
        )

    async def mark_failed(self, *, job_id: str, summary: str) -> None:
        await self._db.importjob.update(
            where={"id": job_id},
            data={"status": "failed", "resultSummary": summary, "errorCount": 1},
        )
