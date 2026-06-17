"""Optional Redis connection for cache, rate limits, and assistant sessions."""

from __future__ import annotations

import logging
from typing import Any

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_redis: Any | None = None
_redis_checked = False


def redis_enabled() -> bool:
    return bool((get_settings().redis_url or "").strip())


async def get_redis() -> Any | None:
    """Return async Redis client or ``None`` when ``REDIS_URL`` is unset."""

    global _redis, _redis_checked
    if _redis_checked:
        return _redis
    _redis_checked = True
    url = (get_settings().redis_url or "").strip()
    if not url:
        return None
    try:
        from redis.asyncio import Redis

        _redis = Redis.from_url(url, decode_responses=True)
        await _redis.ping()
        logger.info("Redis connected")
        return _redis
    except Exception:  # noqa: BLE001
        logger.exception("Redis unavailable — using in-memory fallbacks")
        _redis = None
        return None


async def close_redis() -> None:
    global _redis, _redis_checked
    if _redis is not None:
        await _redis.aclose()
    _redis = None
    _redis_checked = False


def reset_redis_for_tests() -> None:
    global _redis, _redis_checked
    _redis = None
    _redis_checked = False
