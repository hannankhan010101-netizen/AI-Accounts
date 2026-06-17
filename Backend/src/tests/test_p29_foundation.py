"""P29 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest


@pytest.mark.asyncio
async def test_openapi_p29_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/roles/export" in paths
    assert "/api/v1/companies/{company_id}/roles/clone-batch" in paths
    assert "/api/v1/companies/{company_id}/users/{user_id}/resend-invite" in paths
    export_get = paths["/api/v1/companies/{company_id}/roles/export"]["get"]
    assert export_get is not None
    clone_post = paths["/api/v1/companies/{company_id}/roles/clone-batch"]["post"]
    assert clone_post is not None
