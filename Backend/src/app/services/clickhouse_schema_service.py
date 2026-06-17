"""ClickHouse DDL + materialized view for report analytics — P7."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class ClickHouseSchemaService:
    def __init__(self) -> None:
        self._settings = get_settings()

    @property
    def enabled(self) -> bool:
        return bool((self._settings.clickhouse_url or "").strip())

    async def ensure_schema(self) -> dict[str, Any]:
        if not self.enabled:
            return {"ok": False, "message": "CLICKHOUSE_URL not configured"}

        database = (self._settings.clickhouse_database or "default").strip()
        table = (self._settings.clickhouse_table or "report_runs").strip()
        mv = f"{table}_daily_mv"
        statements = [
            f"""
            CREATE TABLE IF NOT EXISTS {database}.{table} (
                company_id String,
                report_id String,
                run_id String,
                row_json String,
                inserted_at DateTime DEFAULT now()
            ) ENGINE = MergeTree()
            ORDER BY (company_id, report_id, run_id)
            """,
            f"""
            CREATE TABLE IF NOT EXISTS {database}.{table}_daily (
                company_id String,
                report_id String,
                run_date Date,
                row_count UInt64
            ) ENGINE = SummingMergeTree()
            ORDER BY (company_id, report_id, run_date)
            """,
            f"""
            CREATE MATERIALIZED VIEW IF NOT EXISTS {database}.{mv}
            TO {database}.{table}_daily
            AS SELECT
                company_id,
                report_id,
                toDate(inserted_at) AS run_date,
                count() AS row_count
            FROM {database}.{table}
            GROUP BY company_id, report_id, run_date
            """,
        ]
        base = self._settings.clickhouse_url.rstrip("/")
        executed: list[str] = []
        async with httpx.AsyncClient(timeout=60.0) as client:
            for sql in statements:
                response = await client.post(f"{base}/", params={"query": sql.strip()})
                if response.status_code >= 400:
                    logger.warning("ClickHouse DDL failed: %s", response.text[:300])
                    return {
                        "ok": False,
                        "error": response.text[:300],
                        "executed": executed,
                    }
                executed.append(sql.strip().split("\n")[0][:80])
        return {
            "ok": True,
            "database": database,
            "table": table,
            "materializedView": mv,
            "executed": executed,
        }
