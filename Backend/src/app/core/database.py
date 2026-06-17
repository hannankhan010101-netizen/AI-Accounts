"""Async Prisma client lifecycle (singleton for the process)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from prisma_generated import Prisma

_prisma: Prisma | None = None
_read_prisma: Prisma | None = None


def get_prisma_client() -> Prisma:
    """
    Return the process-wide Prisma client.

    The client must be connected during application lifespan before use.
    """

    global _prisma
    if _prisma is None:
        _prisma = Prisma()
    return _prisma


def get_read_prisma_client() -> Prisma:
    """Return read-replica client when ``DATABASE_READ_URL`` is configured."""

    global _read_prisma
    from app.core.config import get_settings

    settings = get_settings()
    read_url = (settings.database_read_url or "").strip()
    if not read_url:
        return get_prisma_client()
    if _read_prisma is None:
        _read_prisma = Prisma(datasource={"url": read_url})
    return _read_prisma


@asynccontextmanager
async def prisma_lifespan() -> AsyncIterator[Prisma]:
    """Connect Prisma on entry and disconnect on exit."""

    client = get_prisma_client()
    await client.connect()
    try:
        yield client
    finally:
        await client.disconnect()
