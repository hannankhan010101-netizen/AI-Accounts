"""P40 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest


@pytest.mark.asyncio
async def test_openapi_p40_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    base = "/api/v1/companies/{company_id}"
    assert f"{base}/roles/clone-batch" in paths
    assert "post" in paths[f"{base}/roles/clone-batch"]
    assert f"{base}/users/{{user_id}}/reinvite" in paths
    assert "post" in paths[f"{base}/users/{{user_id}}/reinvite"]
