"""Outbox SKIP LOCKED claim — Phase 1."""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock

import pytest

os.environ.setdefault("SKIP_PRISMA", "1")

from app.repositories.outbox_repository import OutboxRepository
from app.repositories.sql import outbox_queries as oq


def test_claim_sql_uses_skip_locked() -> None:
    assert "SKIP LOCKED" in oq.CLAIM_PENDING_SQL
    assert "FOR UPDATE" in oq.CLAIM_PENDING_SQL


@pytest.mark.asyncio
async def test_claim_pending_fetches_claimed_ids() -> None:
    prisma = MagicMock()
    prisma.query_raw = AsyncMock(return_value=[{"id": "evt-1"}])
    event = MagicMock()
    event.id = "evt-1"
    prisma.outboxevent.find_many = AsyncMock(return_value=[event])
    repo = OutboxRepository(prisma)
    claimed = await repo.claim_pending(limit=5)
    assert len(claimed) == 1
    prisma.query_raw.assert_awaited_once()
    prisma.outboxevent.find_many.assert_awaited_once()
