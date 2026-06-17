"""Scheduled ClickHouse sync for completed report runs — P8."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from prisma_generated import Prisma

from app.services.clickhouse_export_service import ClickHouseExportService

logger = logging.getLogger(__name__)


class ClickHouseSyncService:
    def __init__(self, *, prisma: Prisma) -> None:
        self._db = prisma
        self._export = ClickHouseExportService()

    @property
    def enabled(self) -> bool:
        return self._export.enabled

    async def sync_recent_runs(
        self, *, company_id: str | None = None, days: int = 7
    ) -> dict[str, int]:
        if not self.enabled:
            return {"synced": 0, "skipped": 0}

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        where: dict = {"status": "completed", "completedAt": {"gte": cutoff}}
        if company_id:
            where["companyId"] = company_id

        runs = await self._db.reportrun.find_many(where=where, take=200)
        synced = 0
        for run in runs:
            rows = run.rows if isinstance(run.rows, list) else []
            result = await self._export.export_report_run(
                company_id=run.companyId,
                report_id=run.reportId,
                run_id=run.id,
                rows=rows,
            )
            if result.get("exported"):
                synced += 1
        logger.info("ClickHouse sync completed: %s runs", synced)
        return {"synced": synced, "total": len(runs)}
