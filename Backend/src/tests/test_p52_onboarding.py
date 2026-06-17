"""P52 LLM assistant + platform release CMS tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.services.onboarding_llm_service import _parse_suggestions_json
from app.services.onboarding_release_service import releases_for_user


def test_releases_merge_platform_db_before_catalog() -> None:
    platform = [
        {
            "id": "2026-05-invoice-void",
            "version": "9",
            "title": "Platform DB title",
            "summary": "From DB",
            "publishedAt": "2026-05-01",
            "tourId": None,
            "href": None,
            "permissions": [],
            "isActive": True,
            "source": "platform",
        },
    ]
    merged = releases_for_user(["*"], None, platform)
    hit = next(r for r in merged if r["id"] == "2026-05-invoice-void")
    assert hit["title"] == "Platform DB title"
    assert hit["version"] == "9"


def test_tenant_still_overrides_platform() -> None:
    platform = [
        {
            "id": "custom-key",
            "version": "1",
            "title": "Platform",
            "summary": "P",
            "publishedAt": "2026-01-01",
            "tourId": None,
            "href": None,
            "permissions": [],
            "isActive": True,
            "source": "platform",
        },
    ]
    tenant = [
        {
            "id": "custom-key",
            "version": "2",
            "title": "Tenant",
            "summary": "T",
            "publishedAt": "2026-02-01",
            "tourId": None,
            "href": None,
            "permissions": [],
            "isActive": True,
            "source": "tenant",
        },
    ]
    merged = releases_for_user(["*"], tenant, platform)
    hit = next(r for r in merged if r["id"] == "custom-key")
    assert hit["title"] == "Tenant"


def test_parse_suggestions_json_array() -> None:
    raw = '[{"id":"a","title":"T","reason":"R","score":80,"tourId":"onboard.core"}]'
    out = _parse_suggestions_json(raw)
    assert out and out[0]["id"] == "a"


@pytest.mark.asyncio
async def test_openapi_p52_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/me/onboarding/assistant" in paths
    assert "/api/v1/companies/{company_id}/platform/onboarding/releases" in paths
