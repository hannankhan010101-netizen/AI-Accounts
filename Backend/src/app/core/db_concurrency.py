"""Serialize DB access when Prisma uses a single-connection pool (Supabase :6543)."""

from __future__ import annotations

import asyncio
from urllib.parse import parse_qs, urlparse

_gate: asyncio.Semaphore | None = None


def connection_limit_from_url(database_url: str) -> int | None:
    parsed = urlparse(database_url)
    raw = parse_qs(parsed.query).get("connection_limit", [None])[0]
    if raw is None:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def db_gate_enabled(database_url: str) -> bool:
    """True when the datasource URL caps the pool at one connection."""

    return connection_limit_from_url(database_url) == 1


def get_db_gate() -> asyncio.Semaphore:
    global _gate
    if _gate is None:
        _gate = asyncio.Semaphore(1)
    return _gate
