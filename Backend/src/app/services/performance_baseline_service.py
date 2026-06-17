"""Phase 0/5 measurement — pg_stat_statements and in-process latency baselines."""

from __future__ import annotations

import logging
import time
from typing import Any

from prisma_generated import Prisma

from app.core.metrics import get_metrics

logger = logging.getLogger(__name__)

PG_STAT_TOP_SQL = """
SELECT
  LEFT(query, 200) AS "query",
  calls::bigint AS "calls",
  ROUND(mean_exec_time::numeric, 2) AS "meanMs",
  ROUND(total_exec_time::numeric, 2) AS "totalMs"
FROM pg_stat_statements
WHERE dbid = (SELECT oid FROM pg_database WHERE datname = current_database())
ORDER BY total_exec_time DESC
LIMIT $1
"""


class PerformanceBaselineService:
    def __init__(self, *, prisma: Prisma) -> None:
        self._db = prisma

    async def collect(self) -> dict[str, Any]:
        metrics = get_metrics().snapshot()
        pg_stats = await self.pg_stat_top_queries(limit=15)
        return {
            "httpLatencyMs": metrics.get("httpLatencyMs") or {},
            "histograms": metrics.get("histograms") or {},
            "pgStatStatements": pg_stats,
        }

    async def pg_stat_top_queries(self, *, limit: int = 15) -> list[dict[str, Any]] | None:
        try:
            rows = await self._db.query_raw(PG_STAT_TOP_SQL, limit)
            return [dict(r) for r in rows]
        except Exception:  # noqa: BLE001
            logger.debug("pg_stat_statements unavailable", exc_info=True)
            return None

    async def bench_report_paths(
        self,
        *,
        company_id: str,
        report_service_factory: Any,
    ) -> list[dict[str, Any]]:
        """Time hot report handlers (used by bench script)."""

        from app.services.report_query_service import ReportQueryService

        rpt = ReportQueryService(prisma=self._db)
        cases = (
            ("TB", {}),
            ("032", {}),
            ("033", {}),
            ("GL", {"nominalCode": "1000"}),
            ("GRNI", {}),
            ("AR_AGING", {}),
            ("AP_AGING", {}),
        )
        results: list[dict[str, Any]] = []
        for report_id, criteria in cases:
            started = time.perf_counter()
            try:
                row_count = len(
                    await rpt.execute(
                        company_id=company_id,
                        report_id=report_id,
                        criteria={**criteria, "skipCache": True},
                    )
                )
                ok = True
                error = None
            except Exception as exc:  # noqa: BLE001
                row_count = 0
                ok = False
                error = str(exc)
            elapsed_ms = (time.perf_counter() - started) * 1000
            results.append(
                {
                    "reportId": report_id,
                    "ok": ok,
                    "rowCount": row_count,
                    "elapsedMs": round(elapsed_ms, 2),
                    "error": error,
                }
            )
        return results
