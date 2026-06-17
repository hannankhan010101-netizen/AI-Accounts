"""P55 workflow tours + email digest tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.services.onboarding_digest_service import (
    build_digest_email,
    unread_releases_for_user,
)


def test_unread_releases_respects_dismissed() -> None:
    releases = [{"id": "r1", "title": "T", "summary": "S", "version": "1"}]
    progress = {"dismissedHints": ["release.r1"], "tours": {}}
    assert unread_releases_for_user(releases, progress) == []


def test_build_digest_email_has_titles() -> None:
    subject, text, html = build_digest_email(
        user_name="Alex",
        company_name="Acme",
        releases=[{"id": "r1", "title": "Feature", "summary": "Details", "href": "/dashboard"}],
        app_base_url="http://localhost:3000",
    )
    assert "Feature" in subject or "1" in subject
    assert "Feature" in text
    assert "Feature" in html


@pytest.mark.asyncio
async def test_openapi_p55_digest_route() -> None:
    from app.main import app

    assert "/api/v1/companies/{company_id}/me/onboarding/digest-email" in app.openapi()["paths"]
