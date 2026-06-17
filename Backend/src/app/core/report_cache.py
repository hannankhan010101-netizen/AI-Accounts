"""Versioned Redis cache for catalog report results (Phase 2)."""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from typing import Any

from app.core.config import get_settings
from app.core.redis_client import get_redis

logger = logging.getLogger(__name__)

_LARGE_PAYLOAD_BYTES = 64 * 1024


def _criteria_hash(criteria: dict[str, Any]) -> str:
    normalized = json.dumps(criteria, sort_keys=True, default=str)
    return hashlib.sha256(normalized.encode()).hexdigest()[:24]


def _version_key(company_id: str) -> str:
    return f"report:ver:{company_id}"


def _payload_key(company_id: str, version: int, report_id: str, criteria: dict[str, Any]) -> str:
    return f"report:data:{company_id}:{version}:{report_id}:{_criteria_hash(criteria)}"


class ReportCache:
    async def get_version(self, *, company_id: str) -> int:
        redis = await get_redis()
        if redis is None:
            return 0
        raw = await redis.get(_version_key(company_id))
        return int(raw) if raw else 0

    async def bump_version(self, *, company_id: str) -> None:
        redis = await get_redis()
        if redis is None:
            return
        await redis.incr(_version_key(company_id))

    async def get_rows(
        self,
        *,
        company_id: str,
        report_id: str,
        criteria: dict[str, Any],
    ) -> list[dict[str, Any]] | None:
        redis = await get_redis()
        if redis is None:
            return None
        version = await self.get_version(company_id=company_id)
        key = _payload_key(company_id, version, report_id, criteria)
        raw = await redis.get(key)
        if not raw:
            return None
        try:
            if isinstance(raw, (bytes, bytearray)) and len(raw) > _LARGE_PAYLOAD_BYTES:
                data = await asyncio.to_thread(json.loads, raw)
            elif isinstance(raw, str) and len(raw.encode()) > _LARGE_PAYLOAD_BYTES:
                data = await asyncio.to_thread(json.loads, raw)
            else:
                data = json.loads(raw)
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            logger.warning("Invalid report cache payload for %s", key)
        return None

    async def set_rows(
        self,
        *,
        company_id: str,
        report_id: str,
        criteria: dict[str, Any],
        rows: list[dict[str, Any]],
    ) -> None:
        redis = await get_redis()
        if redis is None:
            return
        ttl = max(60, int(get_settings().report_cache_ttl_seconds or 900))
        version = await self.get_version(company_id=company_id)
        key = _payload_key(company_id, version, report_id, criteria)
        payload = await asyncio.to_thread(json.dumps, rows, default=str)
        await redis.set(key, payload, ex=ttl)


_report_cache = ReportCache()


def get_report_cache() -> ReportCache:
    return _report_cache
