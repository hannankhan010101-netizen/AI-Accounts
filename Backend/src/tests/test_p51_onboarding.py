"""P51 AI suggestions + release CMS tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.services.onboarding_release_service import releases_for_user
from app.services.onboarding_suggestion_service import contextual_suggestions


def test_releases_merge_tenant_over_platform() -> None:
    tenant = [
        {
            "id": "2026-05-invoice-void",
            "version": "2",
            "title": "Custom void title",
            "summary": "Tenant override",
            "publishedAt": "2026-06-01",
            "tourId": None,
            "href": None,
            "permissions": [],
            "isActive": True,
            "source": "tenant",
        },
    ]
    merged = releases_for_user(["*"], tenant)
    hit = next(r for r in merged if r["id"] == "2026-05-invoice-void")
    assert hit["title"] == "Custom void title"
    assert hit["version"] == "2"


def test_contextual_suggestions_route_boost() -> None:
    out = contextual_suggestions(
        pathname="/sales/invoices",
        user_perms=["sales.invoices.create"],
        progress={"tours": {"onboard.core": {"status": "completed"}}, "maturityScore": 10, "dismissedHints": []},
        persona="Sales",
        releases=[],
    )
    assert any("invoice" in s["title"].lower() or s.get("tourId") == "onboard.sell" for s in out)


@pytest.mark.asyncio
async def test_openapi_p51_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/me/onboarding/suggestions" in paths
    assert "/api/v1/companies/{company_id}/onboarding/releases" in paths
