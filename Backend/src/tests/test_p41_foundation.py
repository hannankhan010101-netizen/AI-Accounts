"""P41 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest


@pytest.mark.asyncio
async def test_openapi_p41_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    base = "/api/v1/companies/{company_id}"
    assert f"{base}/users/lookup" in paths
    assert "get" in paths[f"{base}/users/lookup"]
    assert f"{base}/bank-receipts/{{receipt_id}}" in paths
    assert "get" in paths[f"{base}/bank-receipts/{{receipt_id}}"]
