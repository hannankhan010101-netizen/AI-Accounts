"""FBR / digital invoice submission persistence — P4/P8."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from prisma_generated import Prisma
from prisma_generated.models import DigitalInvoiceSubmission


class FbrRepository:
    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def get_for_invoice(
        self, *, company_id: str, sales_invoice_id: str
    ) -> DigitalInvoiceSubmission | None:
        row = await self._db.digitalinvoicesubmission.find_unique(
            where={"salesInvoiceId": sales_invoice_id}
        )
        if row is None or row.companyId != company_id:
            return None
        return row

    async def create_pending(
        self,
        *,
        company_id: str,
        sales_invoice_id: str,
        request_payload: dict[str, Any],
    ) -> DigitalInvoiceSubmission:
        return await self._db.digitalinvoicesubmission.create(
            data={
                "companyId": company_id,
                "salesInvoiceId": sales_invoice_id,
                "status": "pending",
                "requestPayload": request_payload,
            }
        )

    async def mark_submitted(
        self,
        *,
        submission_id: str,
        fbr_reference: str,
        response_payload: dict[str, Any],
    ) -> DigitalInvoiceSubmission:
        return await self._db.digitalinvoicesubmission.update(
            where={"id": submission_id},
            data={
                "status": "submitted",
                "fbrReference": fbr_reference,
                "responsePayload": response_payload,
                "submittedAt": datetime.now(timezone.utc),
                "lastError": None,
                "nextRetryAt": None,
            },
        )

    async def merge_response_payload(
        self,
        *,
        submission_id: str,
        patch: dict[str, Any],
    ) -> DigitalInvoiceSubmission:
        row = await self._db.digitalinvoicesubmission.find_unique(
            where={"id": submission_id}
        )
        existing = row.responsePayload if row and isinstance(row.responsePayload, dict) else {}
        merged = {**existing, **patch}
        return await self._db.digitalinvoicesubmission.update(
            where={"id": submission_id},
            data={"responsePayload": merged},
        )

    async def record_failure(
        self,
        *,
        submission_id: str,
        error_message: str,
        retry_delay_minutes: int = 15,
        max_retries: int = 5,
    ) -> DigitalInvoiceSubmission:
        row = await self._db.digitalinvoicesubmission.find_unique(
            where={"id": submission_id}
        )
        retries = (row.retryCount if row else 0) + 1
        if retries >= max_retries:
            return await self._db.digitalinvoicesubmission.update(
                where={"id": submission_id},
                data={
                    "status": "abandoned",
                    "lastError": error_message[:2000],
                    "retryCount": retries,
                    "nextRetryAt": None,
                },
            )
        return await self._db.digitalinvoicesubmission.update(
            where={"id": submission_id},
            data={
                "status": "error",
                "lastError": error_message[:2000],
                "retryCount": retries,
                "nextRetryAt": datetime.now(timezone.utc)
                + timedelta(minutes=retry_delay_minutes),
            },
        )

    async def list_errors(
        self, *, company_id: str, take: int = 100
    ) -> list[DigitalInvoiceSubmission]:
        return await self._db.digitalinvoicesubmission.find_many(
            where={
                "companyId": company_id,
                "status": {"in": ["error", "pending", "abandoned"]},
            },
            order={"nextRetryAt": "asc"},
            take=take,
        )

    async def list_due_retries(
        self, *, company_id: str | None = None, take: int = 50
    ) -> list[DigitalInvoiceSubmission]:
        where: dict[str, Any] = {
            "status": "error",
            "nextRetryAt": {"lte": datetime.now(timezone.utc)},
        }
        if company_id:
            where["companyId"] = company_id
        return await self._db.digitalinvoicesubmission.find_many(
            where=where,
            take=take,
        )
