"""Assembly templates and jobs — P4."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from prisma_generated import Prisma
from prisma_generated.models import AssemblyJob, AssemblyTemplate


class AssemblyRepository:
    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_templates(self, *, company_id: str) -> list[AssemblyTemplate]:
        return await self._db.assemblytemplate.find_many(
            where={"companyId": company_id, "isActive": True},
            include={"lines": True},
            order={"code": "asc"},
        )

    async def create_template(
        self,
        *,
        company_id: str,
        code: str,
        name: str,
        finished_product_code: str,
        lines: list[dict],
    ) -> AssemblyTemplate:
        return await self._db.assemblytemplate.create(
            data={
                "companyId": company_id,
                "code": code,
                "name": name,
                "finishedProductCode": finished_product_code,
                "lines": {"create": lines},
            },
            include={"lines": True},
        )

    async def list_jobs(self, *, company_id: str, take: int = 100) -> list[AssemblyJob]:
        return await self._db.assemblyjob.find_many(
            where={"companyId": company_id},
            include={"lines": True},
            order={"jobDate": "desc"},
            take=take,
        )

    async def get_job(self, *, company_id: str, job_id: str) -> AssemblyJob | None:
        row = await self._db.assemblyjob.find_unique(
            where={"id": job_id},
            include={"lines": True},
        )
        if row is None or row.companyId != company_id:
            return None
        return row

    async def create_job(
        self,
        *,
        company_id: str,
        job_number: str,
        job_date: datetime,
        template_id: str | None,
        finished_product_code: str,
        quantity: Decimal,
        lines: list[dict],
        batch_number: str | None = None,
        expiry_date: datetime | None = None,
    ) -> AssemblyJob:
        return await self._db.assemblyjob.create(
            data={
                "companyId": company_id,
                "jobNumber": job_number,
                "jobDate": job_date,
                "templateId": template_id,
                "finishedProductCode": finished_product_code,
                "quantity": quantity,
                "status": "draft",
                "batchNumber": batch_number,
                "expiryDate": expiry_date,
                "lines": {"create": lines},
            },
            include={"lines": True},
        )

    async def mark_finished(
        self, *, company_id: str, job_id: str, journal_id: str
    ) -> AssemblyJob:
        row = await self.get_job(company_id=company_id, job_id=job_id)
        if row is None:
            raise ValueError("Assembly job not found")
        return await self._db.assemblyjob.update(
            where={"id": job_id},
            data={"status": "finished", "journalId": journal_id},
            include={"lines": True},
        )
