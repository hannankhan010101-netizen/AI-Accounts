"""P42 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest


@pytest.mark.asyncio
async def test_openapi_p42_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    base = "/api/v1/companies/{company_id}"
    assert f"{base}/users/reinvite" in paths
    assert "post" in paths[f"{base}/users/reinvite"]
    assert f"{base}/bank-payments/{{payment_id}}" in paths
    assert "get" in paths[f"{base}/bank-payments/{{payment_id}}"]


def test_reinvite_by_email_request_model() -> None:
    from app.models.requests.role_requests import ReinviteByEmailRequest

    body = ReinviteByEmailRequest.model_validate(
        {"email": "user@example.com", "roleId": "role-1"}
    )
    assert body.email == "user@example.com"
    assert body.role_id == "role-1"
