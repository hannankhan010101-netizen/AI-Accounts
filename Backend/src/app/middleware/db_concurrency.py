"""Queue HTTP handlers when Prisma cannot serve parallel queries."""

from __future__ import annotations

from fastapi import Request

from app.core.config import get_settings
from app.core.db_concurrency import db_gate_enabled, get_db_gate


async def db_concurrency_middleware(request: Request, call_next):
    settings = get_settings()
    if not db_gate_enabled(settings.database_url):
        return await call_next(request)

    async with get_db_gate():
        return await call_next(request)
