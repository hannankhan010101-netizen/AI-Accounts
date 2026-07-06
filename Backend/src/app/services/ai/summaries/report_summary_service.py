"""AI report summaries — explain a computed report in plain language.

Numbers-in / prose-out: the caller passes an already-computed report payload
(rows/totals produced by the deterministic report services); the LLM only
explains it and must not fabricate or recompute figures. Rows are truncated so a
large report does not blow the context window — the summary is explanatory, not a
data dump. Degrades to ``summary=None`` when no provider is configured.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from app.services.ai.prompts.prompt_registry import get_prompt

logger = logging.getLogger(__name__)

_MAX_ROWS = 60


class AiReportSummaryService:
    def __init__(self, *, provider: Any) -> None:
        self._provider = provider

    async def summarize(
        self,
        *,
        report_title: str,
        rows: list[dict[str, Any]] | None = None,
        totals: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Return {"summary": str|None, "engine": "llm"|"rules"}."""

        if not getattr(self._provider, "enabled", False):
            return {"summary": None, "engine": "rules"}

        payload = {
            "rowCount": len(rows or []),
            "rows": (rows or [])[:_MAX_ROWS],
            "totals": totals or {},
            "truncated": len(rows or []) > _MAX_ROWS,
        }
        prompt = get_prompt("report.summary").render(
            report_title=report_title or "Report",
            payload_json=json.dumps(payload, default=str)[:8000],
        )
        try:
            content, _ = await self._chat(prompt)
        except Exception as exc:
            logger.warning("report summary failed for %s: %s", report_title, exc)
            return {"summary": None, "engine": "rules"}

        summary = (content or "").strip() or None
        return {"summary": summary, "engine": "llm" if summary else "rules"}

    async def _chat(self, prompt: str) -> tuple[str, list[dict[str, Any]]]:
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": "Summarize this report now."},
        ]
        try:
            return await self._provider.chat_completion(
                messages=messages, temperature=0.2, tier="fast"
            )
        except TypeError:
            return await self._provider.chat_completion(messages=messages, temperature=0.2)
