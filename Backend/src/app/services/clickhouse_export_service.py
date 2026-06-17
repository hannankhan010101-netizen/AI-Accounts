"""Export completed report runs to ClickHouse — P6 (optional HTTP insert)."""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class ClickHouseExportService:
    def __init__(self) -> None:
        self._settings = get_settings()

    @property
    def enabled(self) -> bool:
        return bool((self._settings.clickhouse_url or "").strip())

    async def export_report_run(
        self,
        *,
        company_id: str,
        report_id: str,
        run_id: str,
        rows: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if not self.enabled:
            return {"exported": False, "message": "CLICKHOUSE_URL not configured"}

        table = (self._settings.clickhouse_table or "report_runs").strip()
        database = (self._settings.clickhouse_database or "default").strip()
        base = self._settings.clickhouse_url.rstrip("/")
        payload_rows = [
            {
                "company_id": company_id,
                "report_id": report_id,
                "run_id": run_id,
                "row_json": json.dumps(row, default=str),
            }
            for row in rows
            if isinstance(row, dict) and "_meta" not in row
        ]
        if not payload_rows:
            return {"exported": True, "rowCount": 0}

        query = (
            f"INSERT INTO {database}.{table} FORMAT JSONEachRow\n"
            + "\n".join(json.dumps(r) for r in payload_rows)
        )
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{base}/",
                params={"query": query},
                content=query.encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            if response.status_code >= 400:
                logger.warning("ClickHouse export failed: %s", response.text[:500])
                return {
                    "exported": False,
                    "error": response.text[:500],
                }
        return {"exported": True, "rowCount": len(payload_rows)}
