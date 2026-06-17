"""P57 sales receipt workflow + digest helpers + learning surface."""

from __future__ import annotations

import os
from datetime import UTC, datetime

os.environ.setdefault("SKIP_PRISMA", "1")


def test_digest_sent_today_matches_utc_date_prefix() -> None:
    from app.services.onboarding_digest_service import digest_sent_today

    today = datetime.now(UTC).date().isoformat()
    assert digest_sent_today({"preferences": {"lastDigestSentAt": f"{today}T08:00:00Z"}})
    assert not digest_sent_today({"preferences": {"lastDigestSentAt": "2020-01-01T08:00:00Z"}})


def test_digest_is_due_requires_opt_in_and_unread() -> None:
    from app.services.onboarding_digest_service import digest_is_due

    progress = {"preferences": {"emailDigestEnabled": True}, "dismissedHints": [], "tours": {}}
    releases = [{"id": "r1", "title": "T", "summary": "S", "version": "1"}]
    assert digest_is_due(progress, releases)
    assert not digest_is_due(
        {**progress, "preferences": {"emailDigestEnabled": False}},
        releases,
    )


def test_llm_schema_lists_sales_receipt_workflow() -> None:
    from app.services.onboarding_llm_service import SUGGESTION_SCHEMA_HINT

    assert "workflow.sales-receipt" in SUGGESTION_SCHEMA_HINT


def test_suggestions_include_sales_receipt_routes() -> None:
    from app.services.onboarding_suggestion_service import contextual_suggestions

    out = contextual_suggestions(
        pathname="/sales/receipts/new",
        user_perms=["sales.invoices.create"],
        progress={"tours": {}, "dismissedHints": []},
        persona="sales",
        releases=[],
    )
    ids = {s["id"] for s in out}
    assert "ai.route.workflow.sales-receipt" in ids
