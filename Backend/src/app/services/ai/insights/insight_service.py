"""Insight engine v2 — narrate the deterministic dashboard insights with an LLM.

Design guarantee (numbers-in / prose-out): the LLM never computes or invents
figures. The deterministic ``build_insights`` rules run first and are the
authoritative cards; the LLM only writes a short narrative over the
already-computed metrics + cards. If no provider is configured or the call
fails, the service degrades to ``narrative=None`` and returns the rule cards
unchanged — the dashboard still works.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from app.services.ai.prompts.prompt_registry import get_prompt
from app.services.dashboard_insights_service import build_insights

logger = logging.getLogger(__name__)

# Only the numeric essentials go to the model — smaller prompt, less to leak.
_KPI_FIELDS = ("id", "label", "value", "changePct", "status")


class AiInsightService:
    def __init__(self, *, provider: Any) -> None:
        # provider is the task-tier ProviderRouter (or any object exposing
        # ``enabled`` and ``chat_completion``).
        self._provider = provider

    async def narrate(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Return {"cards": [...deterministic...], "narrative": str|None, "engine": str}."""

        cards = build_insights(payload)  # deterministic guardrail — always present

        if not getattr(self._provider, "enabled", False):
            return {"cards": cards, "narrative": None, "engine": "rules"}

        compact = _compact_payload(payload, cards)
        prompt = get_prompt("insight.narration").render(
            payload_json=json.dumps(compact, default=str)[:6000]
        )
        try:
            content, _ = await self._provider.chat_completion(
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": "Write the briefing now."},
                ],
                temperature=0.2,
                tier="fast",
            )
        except TypeError:
            # A bare single provider (no ``tier`` kwarg) instead of the router.
            content, _ = await self._provider.chat_completion(
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": "Write the briefing now."},
                ],
                temperature=0.2,
            )
        except Exception as exc:  # never break the dashboard on an AI failure
            logger.warning("insight narration failed: %s", exc)
            return {"cards": cards, "narrative": None, "engine": "rules"}

        narrative = (content or "").strip() or None
        return {
            "cards": cards,
            "narrative": narrative,
            "engine": "llm" if narrative else "rules",
        }


def _compact_payload(payload: dict[str, Any], cards: list[dict[str, Any]]) -> dict[str, Any]:
    kpis = []
    for k in payload.get("executiveKpis") or []:
        kpis.append({f: k.get(f) for f in _KPI_FIELDS if f in k})
    inv = payload.get("inventoryCommand") or {}
    prof = payload.get("profitability") or {}
    return {
        "period": payload.get("period"),
        "kpis": kpis,
        "overdue": payload.get("overdue"),
        "inventory": {
            "totalValue": inv.get("totalValue"),
            "buckets": inv.get("bucketCounts"),
            "expiringBatches": inv.get("expiringBatches"),
        },
        "profitability": {
            "margins": prof.get("margins"),
            "topExpense": (prof.get("expenseBreakdown") or [None])[0],
        },
        "ruleCards": [
            {"severity": c.get("severity"), "title": c.get("title"), "message": c.get("message")}
            for c in cards
        ],
    }
