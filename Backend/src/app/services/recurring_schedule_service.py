"""Run due recurring schedules — FA §3.3."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.core.exceptions import ValidationAppError
from app.repositories.recurring_schedule_repository import RecurringScheduleRepository
from app.services.batch_document_service import BatchDocumentService
from app.utils.schedule_dates import advance_schedule_date


class RecurringScheduleService:
    def __init__(
        self,
        *,
        repository: RecurringScheduleRepository,
        batch_document_service: BatchDocumentService,
    ) -> None:
        self._repo = repository
        self._batch = batch_document_service

    async def run_due(
        self,
        *,
        company_id: str,
        as_of: datetime | None = None,
        prisma: Any | None = None,
    ) -> dict[str, Any]:
        now = as_of or datetime.now(timezone.utc)
        due = await self._repo.list_due(company_id=company_id, as_of=now)
        executed: list[dict[str, Any]] = []

        for schedule in due:
            if schedule.endDate and schedule.nextRunDate > schedule.endDate:
                await self._repo.update(
                    company_id=company_id,
                    schedule_id=schedule.id,
                    data={"isActive": False},
                )
                continue

            payload = schedule.payload if isinstance(schedule.payload, dict) else {}
            result: dict[str, Any] | None = None

            if schedule.module == "sales_invoice":
                from app.models.requests.sales_requests import (
                    BatchSalesInvoiceCreateRequest,
                )

                body = BatchSalesInvoiceCreateRequest.model_validate(
                    {
                        "invoiceDate": payload.get("invoiceDate") or now.isoformat(),
                        "entries": payload.get("entries") or [],
                        "smartFilters": payload.get("smartFilters"),
                    }
                )
                result = await self._batch.create_batch_sales_invoices(
                    company_id=company_id,
                    invoice_date=body.invoice_date,
                    entries=body.entries,
                    smart_filters=body.smart_filters,
                    prisma=prisma,
                )
            elif schedule.module == "supplier_bill":
                from app.models.requests.purchases_requests import (
                    BatchSupplierBillCreateRequest,
                )

                body = BatchSupplierBillCreateRequest.model_validate(
                    {
                        "billDate": payload.get("billDate") or now.isoformat(),
                        "entries": payload.get("entries") or [],
                        "smartFilters": payload.get("smartFilters"),
                    }
                )
                result = await self._batch.create_batch_supplier_bills(
                    company_id=company_id,
                    bill_date=body.bill_date,
                    entries=body.entries,
                    smart_filters=body.smart_filters,
                    prisma=prisma,
                )
            else:
                raise ValidationAppError(
                    f"Recurring module '{schedule.module}' is not supported yet"
                )

            next_run = advance_schedule_date(
                schedule.nextRunDate,
                frequency=schedule.frequency,
                interval=schedule.interval,
            )
            deactivate = schedule.endDate is not None and next_run > schedule.endDate
            await self._repo.update(
                company_id=company_id,
                schedule_id=schedule.id,
                data={
                    "lastRunAt": now,
                    "nextRunDate": next_run,
                    "isActive": not deactivate,
                },
            )
            executed.append(
                {
                    "scheduleId": schedule.id,
                    "name": schedule.name,
                    "module": schedule.module,
                    "result": result,
                }
            )

        return {"executed": executed, "count": len(executed)}
