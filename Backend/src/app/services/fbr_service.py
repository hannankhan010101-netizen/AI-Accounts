"""FBR digital invoicing — PRAL client, retry queue, error dashboard (P8)."""

from __future__ import annotations

import logging
import uuid
from typing import Any

import httpx

from app.core.config import get_settings
from app.core.exceptions import ValidationAppError
from app.integrations.pral_client import PralClient
from app.repositories.fbr_repository import FbrRepository
from app.repositories.outbox_repository import OutboxRepository
from app.repositories.sales_invoice_repository import SalesInvoiceRepository

logger = logging.getLogger(__name__)

EVENT_FBR_RETRY = "fbr.submission.retry"


class FbrService:
    def __init__(
        self,
        *,
        fbr_repository: FbrRepository,
        sales_invoice_repository: SalesInvoiceRepository,
        outbox_repository: OutboxRepository | None = None,
        pral_client: PralClient | None = None,
    ) -> None:
        self._fbr = fbr_repository
        self._invoices = sales_invoice_repository
        self._outbox = outbox_repository
        self._pral = pral_client or PralClient()
        self._settings = get_settings()

    async def get_status(self, *, company_id: str, sales_invoice_id: str):
        return await self._fbr.get_for_invoice(
            company_id=company_id, sales_invoice_id=sales_invoice_id
        )

    async def list_errors(self, *, company_id: str) -> list[Any]:
        return await self._fbr.list_errors(company_id=company_id)

    async def submit_invoice(self, *, company_id: str, sales_invoice_id: str) -> dict[str, Any]:
        return await self._submit_core(company_id=company_id, sales_invoice_id=sales_invoice_id)

    async def retry_invoice(self, *, company_id: str, sales_invoice_id: str) -> dict[str, Any]:
        row = await self._fbr.get_for_invoice(
            company_id=company_id, sales_invoice_id=sales_invoice_id
        )
        if row is None:
            raise ValidationAppError("No FBR submission to retry")
        if row.status == "submitted":
            raise ValidationAppError("Invoice already submitted")
        return await self._submit_core(
            company_id=company_id,
            sales_invoice_id=sales_invoice_id,
            existing=row,
        )

    async def enqueue_due_retries(self, *, company_id: str) -> int:
        rows = await self._fbr.list_due_retries(company_id=company_id)
        if self._outbox is None:
            return 0
        for row in rows:
            await self._outbox.enqueue(
                company_id=company_id,
                event_type=EVENT_FBR_RETRY,
                payload={"salesInvoiceId": row.salesInvoiceId, "submissionId": row.id},
            )
        return len(rows)

    async def process_retry_event(
        self, *, company_id: str, sales_invoice_id: str
    ) -> None:
        row = await self._fbr.get_for_invoice(
            company_id=company_id, sales_invoice_id=sales_invoice_id
        )
        if row and row.status == "abandoned":
            return
        await self.retry_invoice(
            company_id=company_id, sales_invoice_id=sales_invoice_id
        )

    def _retry_delay_minutes(self, retry_count: int) -> int:
        base = max(1, int(self._settings.fbr_retry_base_minutes))
        delay = base * (2 ** max(0, retry_count - 1))
        return min(delay, 24 * 60)

    async def _submit_core(
        self,
        *,
        company_id: str,
        sales_invoice_id: str,
        existing: Any | None = None,
    ) -> dict[str, Any]:
        invoice = await self._invoices.get_invoice(
            company_id=company_id, invoice_id=sales_invoice_id
        )
        if invoice is None:
            raise ValidationAppError("Sales invoice not found")
        if invoice.status != "posted":
            raise ValidationAppError("Only posted invoices can be submitted to FBR")

        row = existing or await self._fbr.get_for_invoice(
            company_id=company_id, sales_invoice_id=sales_invoice_id
        )
        if row and row.status == "submitted":
            raise ValidationAppError("Invoice already submitted to FBR")

        payload = {
            "invoiceNumber": invoice.invoiceNumber,
            "invoiceDate": invoice.invoiceDate.isoformat(),
            "totalAmount": str(invoice.totalAmount),
            "customerId": invoice.customerId,
        }
        if row is None:
            row = await self._fbr.create_pending(
                company_id=company_id,
                sales_invoice_id=sales_invoice_id,
                request_payload=payload,
            )

        mode = "stub"
        ref = f"FBR-STUB-{uuid.uuid4().hex[:12].upper()}"
        response_payload: dict[str, Any] = {"status": "accepted", "mode": mode}

        if self._pral.enabled:
            try:
                response_payload = await self._pral.submit_invoice(payload=payload)
                ref = str(
                    response_payload.get("fbrReference")
                    or response_payload.get("reference")
                    or ref
                )
                mode = "pral"
            except httpx.HTTPError as exc:
                logger.warning("PRAL submit failed: %s", exc)
                next_retry = (row.retryCount or 0) + 1
                failed = await self._fbr.record_failure(
                    submission_id=row.id,
                    error_message=str(exc),
                    retry_delay_minutes=self._retry_delay_minutes(next_retry),
                    max_retries=self._settings.fbr_max_retry_count,
                )
                if (
                    self._settings.fbr_retry_enabled
                    and self._outbox
                    and failed.status != "abandoned"
                ):
                    await self._outbox.enqueue(
                        company_id=company_id,
                        event_type=EVENT_FBR_RETRY,
                        payload={
                            "salesInvoiceId": sales_invoice_id,
                            "submissionId": row.id,
                        },
                    )
                raise ValidationAppError(
                    f"PRAL submission failed (retry #{failed.retryCount} scheduled): {exc}"
                ) from exc
        else:
            response_payload["mode"] = mode

        submitted = await self._fbr.mark_submitted(
            submission_id=row.id,
            fbr_reference=ref,
            response_payload=response_payload,
        )
        return {
            "submission": submitted,
            "fbrReference": ref,
            "mode": mode,
            "message": "Submitted via PRAL"
            if mode == "pral"
            else "Stub submission. Set FBR_PRAL_ENABLED=1 for live API.",
        }

    async def poll_status(self, *, company_id: str, sales_invoice_id: str) -> dict[str, Any]:
        row = await self._fbr.get_for_invoice(
            company_id=company_id, sales_invoice_id=sales_invoice_id
        )
        if row is None:
            raise ValidationAppError("No FBR submission for this invoice")
        if not row.fbrReference:
            raise ValidationAppError("Submission has no FBR reference yet")

        poll_payload: dict[str, Any]
        mode = "stub"
        if self._pral.enabled:
            try:
                poll_payload = await self._pral.poll_invoice_status(
                    fbr_reference=row.fbrReference
                )
                mode = "pral"
            except httpx.HTTPError as exc:
                poll_payload = {"status": "error", "error": str(exc), "mode": "pral-fallback"}
        else:
            poll_payload = {
                "status": "confirmed",
                "fbrReference": row.fbrReference,
                "mode": "stub",
            }

        updated = await self._fbr.merge_response_payload(
            submission_id=row.id,
            patch={"lastPoll": poll_payload, "pollMode": mode},
        )
        return {
            "submission": updated,
            "poll": poll_payload,
            "mode": mode,
        }
