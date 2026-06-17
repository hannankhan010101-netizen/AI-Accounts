"""Pending tool-call sessions (resume after client tools) — memory or Redis."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any

_TTL_SECONDS = 600


@dataclass
class PendingAssistantSession:
    messages: list[dict[str, Any]]
    mode: str
    pathname: str
    company_id: str
    user_id: str
    permissions: list[str]
    locale: str | None
    tool_call_id: str
    tool_name: str
    created_at: float = field(default_factory=time.monotonic)


_sessions: dict[str, PendingAssistantSession] = {}


def _redis_key(key: str) -> str:
    return f"assistant:session:{key}"


async def store_session(key: str, session: PendingAssistantSession) -> None:
    from app.core.redis_client import get_redis

    redis = await get_redis()
    if redis is not None:
        payload = asdict(session)
        await redis.set(_redis_key(key), json.dumps(payload), ex=_TTL_SECONDS)
        return
    _purge_expired()
    _sessions[key] = session


async def pop_session(key: str) -> PendingAssistantSession | None:
    from app.core.redis_client import get_redis

    redis = await get_redis()
    if redis is not None:
        raw = await redis.getdel(_redis_key(key))
        if not raw:
            return None
        data = json.loads(raw)
        return PendingAssistantSession(**data)

    _purge_expired()
    return _sessions.pop(key, None)


def _purge_expired() -> None:
    now = time.monotonic()
    expired = [k for k, v in _sessions.items() if now - v.created_at > _TTL_SECONDS]
    for k in expired:
        _sessions.pop(k, None)


def reset_for_tests() -> None:
    _sessions.clear()
