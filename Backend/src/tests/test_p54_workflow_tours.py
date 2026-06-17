"""P54 workflow tour definitions (frontend registry mirrored in OpenAPI docs)."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")


def test_workflow_tour_ids_documented() -> None:
    """Workflow tour ids used by assistant LLM schema hint."""
    expected = {"workflow.sales-invoice", "workflow.supplier-bill"}
    from app.services.onboarding_llm_service import SUGGESTION_SCHEMA_HINT

    for tid in expected:
        assert tid in SUGGESTION_SCHEMA_HINT
