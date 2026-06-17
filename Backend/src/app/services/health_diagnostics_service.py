"""Aggregated readiness and ops diagnostics (Phase 4)."""

from __future__ import annotations

import asyncio
import os
from typing import Any

from prisma_generated import Prisma

from app.constants.report_catalog_registry import catalog_coverage
from app.core.config import get_settings
from app.core.metrics import get_metrics
from app.core.redis_client import get_redis, redis_enabled
from app.repositories.outbox_repository import OutboxRepository
from app.services.performance_baseline_service import PerformanceBaselineService


class HealthDiagnosticsService:
    def __init__(self, *, prisma: Prisma) -> None:
        self._db = prisma

    async def collect(self) -> dict[str, Any]:
        settings = get_settings()
        backlog_max = int(getattr(settings, "outbox_backlog_max", 10_000) or 10_000)

        outbox_pending, mv_status, db_ok, redis_status = await asyncio.gather(
            OutboxRepository(self._db).count_pending(),
            self._materialized_view_status(),
            self._ping_database(),
            self._redis_status(),
        )

        perf: dict[str, object] = {
            "httpLatencyMs": get_metrics().latency_percentiles(),
        }
        if settings.perf_expose_pg_stat:
            perf["pgStatStatements"] = await PerformanceBaselineService(
                prisma=self._db
            ).pg_stat_top_queries(limit=10)

        return {
            "status": "ok" if db_ok and outbox_pending <= backlog_max else "degraded",
            "database": "ok" if db_ok else "error",
            "redis": redis_status,
            "outboxPending": outbox_pending,
            "outboxBacklogMax": backlog_max,
            "materializedViews": mv_status,
            "appMode": (settings.app_mode or "all").strip().lower(),
            "reportCatalog": catalog_coverage(),
            "metrics": get_metrics().snapshot(),
            "performance": perf,
        }

    async def _redis_status(self) -> str:
        if not redis_enabled():
            return "disabled"
        client = await get_redis()
        return "ok" if client is not None else "unavailable"

    async def _ping_database(self) -> bool:
        if os.getenv("SKIP_PRISMA") == "1":
            return True
        try:
            await self._db.query_raw("SELECT 1 AS ok")
            return True
        except Exception:  # noqa: BLE001
            return False

    async def _materialized_view_status(self) -> dict[str, str]:
        views = ("mv_nominal_balances", "mv_ar_customer_open", "mv_ap_supplier_open")

        async def _probe(name: str) -> tuple[str, str]:
            try:
                await self._db.query_raw(f'SELECT 1 FROM "{name}" LIMIT 1')
                return name, "ok"
            except Exception:  # noqa: BLE001
                return name, "missing_or_empty"

        pairs = await asyncio.gather(*(_probe(name) for name in views))
        return dict(pairs)
