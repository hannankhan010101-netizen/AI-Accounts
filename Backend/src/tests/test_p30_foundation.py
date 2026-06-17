"""P30 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.constants.invite_email_defaults import DEFAULT_INVITE_EMAIL_TEMPLATE
from app.services.invite_email_template_service import apply_placeholders


def test_apply_placeholders_replaces_tokens() -> None:
    out = apply_placeholders(
        DEFAULT_INVITE_EMAIL_TEMPLATE,
        companyName="Acme Ltd",
        resetLink="https://app.example/reset",
        code="123456",
        ttlMinutes="15",
    )
    assert "Acme Ltd" in out["subject"]
    assert "123456" in out["introText"]
    assert "https://app.example/reset" in out["introHtml"]


@pytest.mark.asyncio
async def test_openapi_p30_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/roles/import" in paths
    assert "/api/v1/companies/{company_id}/settings/invite-email-template" in paths
