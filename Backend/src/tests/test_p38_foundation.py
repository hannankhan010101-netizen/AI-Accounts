"""P38 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest


@pytest.mark.asyncio
async def test_openapi_p38_invite_template_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    base = "/api/v1/companies/{company_id}/settings"
    assert f"{base}/invite-email-template" in paths
    assert "put" in paths[f"{base}/invite-email-template"]
    assert f"{base}/welcome-email-template" in paths
    assert "put" in paths[f"{base}/welcome-email-template"]


@pytest.mark.asyncio
async def test_openapi_p38_role_clone_route() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    clone = "/api/v1/companies/{company_id}/roles/{role_id}/clone"
    assert clone in paths
    assert "post" in paths[clone]
