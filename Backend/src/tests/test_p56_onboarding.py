"""P56 bank payment workflow + digest scheduling helpers."""

from __future__ import annotations

import os
from datetime import UTC, datetime

os.environ.setdefault("SKIP_PRISMA", "1")


def test_digest_progress_view_includes_preferences() -> None:
    from app.api.routes.tenant import _onboarding_progress_view

    view = _onboarding_progress_view(
        {
            "tours": {},
            "maturityScore": 5,
            "dismissedHints": [],
            "preferences": {"emailDigestEnabled": True, "lastDigestSentAt": "2026-05-22T12:00:00Z"},
        }
    )
    assert view["preferences"]["emailDigestEnabled"] is True
    assert "2026-05-22" in view["preferences"]["lastDigestSentAt"]


def test_unread_skips_dismissed_release_keys() -> None:
    from app.services.onboarding_digest_service import unread_releases_for_user

    unread = unread_releases_for_user(
        [{"id": "x", "title": "T", "summary": "S", "version": "1"}],
        {"dismissedHints": ["release.x"], "tours": {}},
    )
    assert unread == []


def test_llm_schema_lists_bank_payment_workflow() -> None:
    from app.services.onboarding_llm_service import SUGGESTION_SCHEMA_HINT

    assert "workflow.bank-payment" in SUGGESTION_SCHEMA_HINT
