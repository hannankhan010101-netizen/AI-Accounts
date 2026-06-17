"""P50 release feed + onboarding insights tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.services.onboarding_release_service import (
    insights_from_payloads,
    releases_for_user,
)


def test_releases_for_user_filters_permissions() -> None:
    all_releases = releases_for_user(["*"])
    assert len(all_releases) >= 2
    bank_only = releases_for_user(["bank.reconciliation.create"])
    assert any(r["id"] == "2026-05-bank-recon-complete" for r in bank_only)
    assert not any(r["id"] == "2026-05-invoice-void" for r in bank_only)


def test_insights_from_payloads() -> None:
    payloads = [
        {
            "eventLog": [
                {"event": "tour_started", "tourId": "onboard.core"},
                {"event": "step_viewed", "tourId": "onboard.core", "stepId": "nav"},
                {"event": "tour_completed", "tourId": "onboard.core"},
            ],
        },
    ]
    out = insights_from_payloads(payloads)
    assert out["usersWithActivity"] == 1
    assert out["tourCompletion"][0]["tourId"] == "onboard.core"
    assert out["tourCompletion"][0]["ratePercent"] == 100


@pytest.mark.asyncio
async def test_openapi_p50_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/onboarding/insights" in paths
    base = "/api/v1/companies/{company_id}/me/onboarding"
    assert "get" in paths[base]
