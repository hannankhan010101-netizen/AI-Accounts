"""Smoke tests that do not require a live database."""

from __future__ import annotations

import os

import pytest
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("SKIP_PRISMA", "1")

from app.main import app


@pytest.mark.asyncio
async def test_health_returns_ok() -> None:
    """GET /health should return 200."""

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_report_definitions_seed_non_empty() -> None:
    """Seeded report catalog from feature doc should not be empty."""

    from app.constants.report_definitions import all_report_definitions

    assert len(all_report_definitions()) >= 40
