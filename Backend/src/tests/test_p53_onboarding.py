"""P53 tour discoverability + insights export tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.services.onboarding_insights_csv import insights_to_csv


def test_insights_csv_contains_headers() -> None:
    text = insights_to_csv(
        {
            "totalLearners": 2,
            "usersWithActivity": 1,
            "tourCompletion": [{"tourId": "onboard.core", "started": 3, "completed": 1, "ratePercent": 33}],
            "topStepViews": [{"step": "onboard.core:workspace", "views": 5}],
        }
    )
    assert "tourId" in text
    assert "onboard.core" in text


@pytest.mark.asyncio
async def test_openapi_p53_insights_export() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/onboarding/insights/export" in paths
