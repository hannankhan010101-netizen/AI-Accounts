"""Refresh and read Postgres materialized views (Phase 3)."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from prisma_generated import Prisma

from app.repositories.sql import materialized_view_queries as mvq

logger = logging.getLogger(__name__)


def _as_decimal(value: Any) -> Decimal:
    if value is None:
        return Decimal(0)
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


class MaterializedViewService:
    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def refresh_all(self) -> dict[str, bool]:
        results: dict[str, bool] = {}
        for name, sql in (
            ("mv_nominal_balances", mvq.REFRESH_MV_NOMINAL),
            ("mv_ar_customer_open", mvq.REFRESH_MV_AR),
            ("mv_ap_supplier_open", mvq.REFRESH_MV_AP),
        ):
            try:
                await self._db.execute_raw(sql)
                results[name] = True
            except Exception:  # noqa: BLE001
                logger.exception("MV refresh failed: %s", name)
                results[name] = False
        return results

    async def trial_balance_from_mv(self, *, company_id: str) -> list[dict] | None:
        try:
            raw = await self._db.query_raw(mvq.TRIAL_BALANCE_FROM_MV_SQL, company_id)
        except Exception:  # noqa: BLE001
            logger.debug("mv_nominal_balances not available", exc_info=True)
            return None
        return [
            {
                "nominalCode": row["nominalCode"],
                "name": row.get("name"),
                "debit": str(_as_decimal(row.get("debit"))),
                "credit": str(_as_decimal(row.get("credit"))),
                "balance": str(_as_decimal(row.get("balance"))),
            }
            for row in raw
        ]

    async def ar_aging_rows_from_mv(self, *, company_id: str) -> list[dict] | None:
        try:
            return await self._db.query_raw(mvq.AR_AGING_FROM_MV_SQL, company_id)
        except Exception:  # noqa: BLE001
            logger.debug("mv_ar_customer_open not available", exc_info=True)
            return None

    async def ap_aging_rows_from_mv(self, *, company_id: str) -> list[dict] | None:
        try:
            return await self._db.query_raw(mvq.AP_AGING_FROM_MV_SQL, company_id)
        except Exception:  # noqa: BLE001
            logger.debug("mv_ap_supplier_open not available", exc_info=True)
            return None
