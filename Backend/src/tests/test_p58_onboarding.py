"""P58 supplier payment workflow tour."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")


def test_llm_schema_lists_supplier_payment_workflow() -> None:
    from app.services.onboarding_llm_service import SUGGESTION_SCHEMA_HINT

    assert "workflow.supplier-payment" in SUGGESTION_SCHEMA_HINT


def test_suggestions_include_supplier_payment_routes() -> None:
    from app.services.onboarding_suggestion_service import contextual_suggestions

    out = contextual_suggestions(
        pathname="/purchases/payments/new",
        user_perms=["purchases.bills.create"],
        progress={"tours": {}, "dismissedHints": []},
        persona="procurement",
        releases=[],
    )
    ids = {s["id"] for s in out}
    assert "ai.route.workflow.supplier-payment" in ids
