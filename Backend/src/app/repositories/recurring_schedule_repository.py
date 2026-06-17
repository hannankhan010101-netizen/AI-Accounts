"""Recurring document schedules — FA §3.3."""

from __future__ import annotations

from typing import Any

from prisma_generated import Prisma
from prisma_generated.models import RecurringSchedule


class RecurringScheduleRepository:
    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def list_for_company(
        self, *, company_id: str, take: int = 200
    ) -> list[RecurringSchedule]:
        return await self._db.recurringschedule.find_many(
            where={"companyId": company_id},
            order={"nextRunDate": "asc"},
            take=take,
        )

    async def get_by_id(
        self, *, company_id: str, schedule_id: str
    ) -> RecurringSchedule | None:
        row = await self._db.recurringschedule.find_unique(where={"id": schedule_id})
        if row is None or row.companyId != company_id:
            return None
        return row

    async def create(
        self,
        *,
        company_id: str,
        name: str,
        module: str,
        frequency: str,
        interval: int,
        next_run_date: Any,
        end_date: Any | None,
        is_active: bool,
        payload: dict[str, Any],
    ) -> RecurringSchedule:
        return await self._db.recurringschedule.create(
            data={
                "companyId": company_id,
                "name": name,
                "module": module,
                "frequency": frequency,
                "interval": interval,
                "nextRunDate": next_run_date,
                "endDate": end_date,
                "isActive": is_active,
                "payload": payload,
            }
        )

    async def update(
        self,
        *,
        company_id: str,
        schedule_id: str,
        data: dict[str, Any],
    ) -> RecurringSchedule:
        row = await self.get_by_id(company_id=company_id, schedule_id=schedule_id)
        if row is None:
            raise ValueError("Recurring schedule not found")
        return await self._db.recurringschedule.update(
            where={"id": schedule_id},
            data=data,
        )

    async def delete(self, *, company_id: str, schedule_id: str) -> None:
        row = await self.get_by_id(company_id=company_id, schedule_id=schedule_id)
        if row is None:
            raise ValueError("Recurring schedule not found")
        await self._db.recurringschedule.delete(where={"id": schedule_id})

    async def list_due(
        self, *, company_id: str, as_of: Any, take: int = 50
    ) -> list[RecurringSchedule]:
        return await self._db.recurringschedule.find_many(
            where={
                "companyId": company_id,
                "isActive": True,
                "nextRunDate": {"lte": as_of},
            },
            order={"nextRunDate": "asc"},
            take=take,
        )
