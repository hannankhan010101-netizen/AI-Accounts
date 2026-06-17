"""Assembly template and job orchestration — P4."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from app.core.exceptions import ValidationAppError
from app.domain import document_workflow as wf
from prisma_generated.models import AssemblyJob

from app.repositories.assembly_repository import AssemblyRepository
from app.repositories.product_repository import ProductRepository
from app.services.document_number_service import DocumentNumberService
from app.services.posting_prerequisites_service import PostingPrerequisitesService
from app.services.posting_service import PostingService


class AssemblyService:
    def __init__(
        self,
        *,
        assembly_repository: AssemblyRepository,
        product_repository: ProductRepository,
        document_number_service: DocumentNumberService,
        posting_service: PostingService,
        prerequisites: PostingPrerequisitesService,
    ) -> None:
        self._assembly = assembly_repository
        self._products = product_repository
        self._numbers = document_number_service
        self._posting = posting_service
        self._prereq = prerequisites

    async def list_templates(self, *, company_id: str):
        return await self._assembly.list_templates(company_id=company_id)

    async def create_template(
        self,
        *,
        company_id: str,
        code: str,
        name: str,
        finished_product_code: str,
        lines: list[dict],
    ):
        return await self._assembly.create_template(
            company_id=company_id,
            code=code,
            name=name,
            finished_product_code=finished_product_code,
            lines=lines,
        )

    async def list_jobs(self, *, company_id: str):
        return await self._assembly.list_jobs(company_id=company_id)

    async def get_job(self, *, company_id: str, job_id: str) -> AssemblyJob | None:
        return await self._assembly.get_job(company_id=company_id, job_id=job_id)

    async def create_job_from_template(
        self,
        *,
        company_id: str,
        template_id: str,
        job_date: datetime,
        quantity: Decimal,
        batch_number: str | None = None,
        expiry_date: datetime | None = None,
    ):
        templates = await self._assembly.list_templates(company_id=company_id)
        template = next((t for t in templates if t.id == template_id), None)
        if template is None:
            raise ValidationAppError("Assembly template not found")
        products = await self._products.get_by_codes(
            company_id=company_id,
            codes=[line.componentProductCode for line in template.lines or []],
        )
        by_code = {p.code: p for p in products}
        job_lines: list[dict] = []
        for line in template.lines or []:
            prod = by_code.get(line.componentProductCode)
            unit = Decimal(str(prod.cost)) if prod else Decimal(0)
            job_lines.append(
                {
                    "componentProductCode": line.componentProductCode,
                    "quantity": Decimal(str(line.quantity)) * quantity,
                    "unitCost": unit,
                }
            )
        job_number = str(
            await self._numbers.reserve_next(company_id=company_id, sequence_key="AJ")
        )
        return await self._assembly.create_job(
            company_id=company_id,
            job_number=job_number,
            job_date=job_date,
            template_id=template_id,
            finished_product_code=template.finishedProductCode,
            quantity=quantity,
            lines=job_lines,
            batch_number=batch_number,
            expiry_date=expiry_date,
        )

    async def finish_job(self, *, company_id: str, job_id: str) -> AssemblyJob:
        job = await self._assembly.get_job(company_id=company_id, job_id=job_id)
        if job is None:
            raise ValidationAppError("Assembly job not found")
        if job.status == "finished":
            raise ValidationAppError("Assembly job is already finished")
        if job.journalId:
            raise ValidationAppError("Assembly job is already posted")

        total = Decimal(0)
        for line in job.lines or []:
            total += Decimal(str(line.quantity)) * Decimal(str(line.unitCost))
        if total <= 0:
            raise ValidationAppError("Assembly job has zero cost")

        d = await self._prereq.require_stock_adjustment_posting(company_id=company_id)
        inv_code = d["inventoryNominalCode"]

        journal_lines: list[dict] = [
            {"nominalCode": inv_code, "debit": total, "credit": Decimal(0)},
        ]
        for line in job.lines or []:
            line_amount = Decimal(str(line.quantity)) * Decimal(str(line.unitCost))
            if line_amount <= 0:
                continue
            journal_lines.append(
                {
                    "nominalCode": inv_code,
                    "debit": Decimal(0),
                    "credit": line_amount,
                    "projectCode": line.componentProductCode,
                }
            )

        journal = await self._posting.create_traced_journal(
            company_id=company_id,
            journal_date=job.jobDate,
            ref_no=f"ASM {job.jobNumber}",
            lines=journal_lines,
            source_type=wf.SOURCE_ASSEMBLY_JOB,
            source_id=job.id,
        )
        finished = await self._assembly.mark_finished(
            company_id=company_id, job_id=job_id, journal_id=journal.id
        )
        batch_number = getattr(job, "batchNumber", None)
        if batch_number:
            from datetime import datetime, timezone

            batch_no = str(batch_number).strip()
            qty = Decimal(str(job.quantity))
            expiry = getattr(job, "expiryDate", None)
            existing = await self._assembly._db.productbatch.find_first(
                where={
                    "companyId": company_id,
                    "productCode": job.finishedProductCode,
                    "batchNumber": batch_no,
                }
            )
            data = {
                "quantityOnHand": qty,
                "expiryDate": expiry,
                "notes": f"Assembly job {job.jobNumber}",
            }
            if existing:
                await self._assembly._db.productbatch.update(
                    where={"id": existing.id}, data=data
                )
            else:
                await self._assembly._db.productbatch.create(
                    data={
                        "companyId": company_id,
                        "productCode": job.finishedProductCode,
                        "batchNumber": batch_no,
                        **data,
                    }
                )
        return finished
