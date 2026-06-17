"""P48 onboarding / tour progress API tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest


@pytest.mark.asyncio
async def test_openapi_p48_onboarding_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    base = "/api/v1/companies/{company_id}/me/onboarding"
    assert base in paths
    assert "get" in paths[base]
    assert "put" in paths[base]
    events = f"{base}/events"
    assert events in paths
    assert "post" in paths[events]
