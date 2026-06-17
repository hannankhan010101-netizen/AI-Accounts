"""P39 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.services.invite_email_template_service import apply_placeholders
from app.constants.invite_email_defaults import DEFAULT_INVITE_EMAIL_TEMPLATE


def test_apply_placeholders_renders_invite() -> None:
    out = apply_placeholders(
        DEFAULT_INVITE_EMAIL_TEMPLATE,
        companyName="Acme",
        resetLink="https://x.test/reset",
        code="999",
        ttlMinutes="10",
    )
    assert "Acme" in out["subject"]
    assert "999" in out["introText"]
    assert "x.test" in out["introHtml"]


@pytest.mark.asyncio
async def test_openapi_p39_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    base = "/api/v1/companies/{company_id}"
    assert f"{base}/settings/invite-email-template/preview" in paths
    users_get = paths[f"{base}/users"]["get"]
    param_names = {p["name"] for p in users_get.get("parameters", [])}
    assert "userId" in param_names
