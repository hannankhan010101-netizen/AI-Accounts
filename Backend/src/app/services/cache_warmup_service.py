"""Pre-warm hot read paths after deploy or MV refresh (Phase 4)."""

from __future__ import annotations

import asyncio
import logging

from prisma_generated import Prisma

from app.core.config import get_settings
from app.core.report_cache import get_report_cache
from app.repositories.dashboard_overview_repository import DashboardOverviewRepository
from app.repositories.dashboard_repository import DashboardRepository
from app.services.materialized_view_service import MaterializedViewService
from app.services.report_query_service import ReportQueryService

logger = logging.getLogger(__name__)


class CacheWarmupService:
    def __init__(self, *, prisma: Prisma, read_prisma: Prisma | None = None) -> None:
        self._db = read_prisma or prisma
        self._primary = prisma

    async def warm_company(self, *, company_id: str) -> dict[str, object]:
        stats: dict[str, object] = {"companyId": company_id}
        rpt = ReportQueryService(prisma=self._db)
        cache = get_report_cache()

        async def _warm_report(report_id: str, criteria: dict) -> bool:
            try:
                rows = await rpt.execute(
                    company_id=company_id,
                    report_id=report_id,
                    criteria=criteria,
                )
                await cache.set_rows(
                    company_id=company_id,
                    report_id=report_id,
                    criteria=criteria,
                    rows=rows,
                )
                return True
            except Exception:  # noqa: BLE001
                logger.exception(
                    "Report warm failed company=%s report=%s", company_id, report_id
                )
                return False

        async def _warm_dashboard() -> bool:
            try:
                await DashboardRepository(self._db).summary(company_id=company_id)
                return True
            except Exception:  # noqa: BLE001
                logger.exception("Dashboard warm failed for %s", company_id)
                return False

        async def _warm_overview() -> bool:
            try:
                await DashboardOverviewRepository(self._db).overview(
                    company_id=company_id
                )
                return True
            except Exception:  # noqa: BLE001
                logger.exception("Overview warm failed for %s", company_id)
                return False

        (
            dashboard_ok,
            overview_ok,
            tb_ok,
            inv_ok,
            fin_cmp_ok,
        ) = await asyncio.gather(
            _warm_dashboard(),
            _warm_overview(),
            _warm_report("TB", {}),
            _warm_report("028", {"pageSize": 200}),
            _warm_report("FIN_CMP", {"periodCount": 12}),
        )
        stats["dashboard"] = dashboard_ok
        stats["overview"] = overview_ok
        stats["reportsWarmed"] = sum(1 for ok in (tb_ok, inv_ok, fin_cmp_ok) if ok)
        return stats

    async def warm_configured_companies(self) -> list[dict[str, object]]:
        raw = (get_settings().cache_warm_company_ids or "").strip()
        if not raw:
            return []
        company_ids = [c.strip() for c in raw.split(",") if c.strip()]
        return await asyncio.gather(
            *(self.warm_company(company_id=company_id) for company_id in company_ids)
        )

    async def refresh_materialized_views(self) -> dict[str, bool]:
        return await MaterializedViewService(self._primary).refresh_all()
