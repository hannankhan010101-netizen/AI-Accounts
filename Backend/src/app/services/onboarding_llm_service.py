"""Optional LLM layer for learning assistant — P52; uses Groq when configured."""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx
from groq.types.chat import ChatCompletionMessageParam

from app.core.config import get_settings
from app.integrations.groq_client import GroqClient
from app.services.assistant.prompt_sanitize import sanitize_user_message
from app.services.onboarding_suggestion_service import contextual_suggestions

logger = logging.getLogger(__name__)

SUGGESTION_SCHEMA_HINT = """
Return ONLY a JSON array (max 6 items). Each item:
{"id":"string","title":"string","reason":"string","score":0-100,"tourId":"optional","href":"optional"}
Use tourId values only from this list when relevant:
onboard.core, onboard.sell, onboard.money, onboard.buy, onboard.admin,
onboard.stock, onboard.reports,
workflow.sales-invoice, workflow.sales-receipt, workflow.supplier-bill, workflow.supplier-payment, workflow.journal, workflow.bank-receipt, workflow.bank-payment,
release.invoice-void, release.bank-recon
"""


def _legacy_llm_configured() -> bool:
    settings = get_settings()
    return settings.onboarding_llm_enabled and bool(settings.onboarding_llm_api_key.strip())


def _groq_configured() -> bool:
    return GroqClient().enabled


def _any_llm_configured() -> bool:
    return _groq_configured() or _legacy_llm_configured()


async def learning_suggestions(
    *,
    pathname: str,
    user_perms: list[str],
    progress: dict[str, Any],
    persona: str | None,
    releases: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], str]:
    """Rules first; optional LLM rerank/rewrite when configured."""

    rules = contextual_suggestions(
        pathname=pathname,
        user_perms=user_perms,
        progress=progress,
        persona=persona,
        releases=releases,
    )
    if not _any_llm_configured():
        return rules, "rules"

    try:
        llm = await _fetch_llm_suggestions(
            pathname=pathname,
            user_perms=user_perms,
            progress=progress,
            persona=persona,
            releases=releases,
            rule_seed=rules,
        )
        if llm:
            engine = "groq" if _groq_configured() else "llm"
            return llm, engine
    except Exception as exc:
        logger.warning("onboarding LLM fallback to rules: %s", exc)

    return rules, "rules"


async def assistant_reply(
    *,
    message: str,
    pathname: str,
    user_perms: list[str],
    progress: dict[str, Any],
    persona: str | None,
) -> tuple[str, str]:
    """Short natural-language answer for the onboarding assistant chat box."""

    if not _any_llm_configured():
        return (
            "AI assistant is not configured on this server. Use the suggested actions below "
            "or open guided tours from the compass button.",
            "rules",
        )

    if _groq_configured():
        from app.services.assistant.orchestrator import AssistantOrchestrator
        from app.integrations.groq_client import GroqClient
        from app.repositories.assistant_conversation_repository import (
            AssistantConversationRepository,
        )
        from app.services.assistant.tool_handlers import AssistantToolHandlers

        orch = AssistantOrchestrator(
            groq_client=GroqClient(),
            conversation_repository=_NoopConversationRepo(),
            tool_handlers=_NoopToolHandlers(),
            audit_log_service=_NoopAudit(),
        )
        return await orch.simple_reply(
            message=message,
            pathname=pathname,
            permissions=user_perms,
            mode="onboarding",
            onboarding_progress=progress,
        )

    settings = get_settings()
    system = (
        "You are a concise onboarding coach for Fast Accounts accounting software. "
        "Answer in 2-4 sentences. Suggest concrete next steps and mention tours when helpful. "
        "Do not invent features outside sales, purchases, bank, inventory, settings, reports."
    )
    user = json.dumps(
        {
            "question": sanitize_user_message(
                message, max_chars=settings.assistant_max_message_chars
            )[:500],
            "pathname": pathname,
            "persona": persona,
            "maturityScore": progress.get("maturityScore", 0),
            "completedTours": [
                k
                for k, v in (progress.get("tours") or {}).items()
                if isinstance(v, dict) and v.get("status") == "completed"
            ],
        }
    )
    try:
        text = await _legacy_chat_completion(system=system, user=user)
        return text.strip() or "I could not generate a reply.", "llm"
    except Exception as exc:
        logger.warning("assistant_reply failed: %s", exc)
        return (
            "I could not reach the AI service. Try a guided tour from the list below.",
            "rules",
        )


class _NoopConversationRepo:
    async def create_thread(self, **kwargs: Any) -> str:
        return "noop"

    async def append_message(self, **kwargs: Any) -> str:
        return "noop"

    async def recent_turns_for_llm(self, **kwargs: Any) -> list:
        return []


class _NoopToolHandlers:
    async def execute(self, **kwargs: Any) -> dict:
        return {}


class _NoopAudit:
    async def record(self, **kwargs: Any) -> None:
        return None


async def _fetch_llm_suggestions(
    *,
    pathname: str,
    user_perms: list[str],
    progress: dict[str, Any],
    persona: str | None,
    releases: list[dict[str, Any]],
    rule_seed: list[dict[str, Any]],
) -> list[dict[str, Any]] | None:
    system = "You personalize Fast Accounts onboarding. " + SUGGESTION_SCHEMA_HINT
    user = json.dumps(
        {
            "pathname": pathname,
            "persona": persona,
            "permissions": user_perms[:40],
            "progress": progress,
            "releases": releases[:5],
            "ruleSuggestions": rule_seed,
        },
        default=str,
    )[:6000]
    raw = await _chat_completion(system=system, user=user)
    return _parse_suggestions_json(raw)


async def _chat_completion(*, system: str, user: str) -> str:
    if _groq_configured():
        client = GroqClient()
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        content, _ = await client.chat_completion(messages=messages, tools=None)
        return content
    return await _legacy_chat_completion(system=system, user=user)


async def _legacy_chat_completion(*, system: str, user: str) -> str:
    settings = get_settings()
    base = settings.onboarding_llm_base_url.rstrip("/")
    url = f"{base}/chat/completions"
    payload = {
        "model": settings.onboarding_llm_model,
        "temperature": 0.3,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    headers = {
        "Authorization": f"Bearer {settings.onboarding_llm_api_key}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=settings.onboarding_llm_timeout_seconds) as client:
        res = await client.post(url, headers=headers, json=payload)
        res.raise_for_status()
        data = res.json()
    choices = data.get("choices") or []
    if not choices:
        return ""
    msg = choices[0].get("message") or {}
    content = msg.get("content")
    return str(content) if content else ""


def _parse_suggestions_json(raw: str) -> list[dict[str, Any]] | None:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if len(lines) > 2 else lines)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("[")
        end = text.rfind("]")
        if start < 0 or end <= start:
            return None
        parsed = json.loads(text[start : end + 1])
    if not isinstance(parsed, list):
        return None
    out: list[dict[str, Any]] = []
    for i, item in enumerate(parsed[:6]):
        if not isinstance(item, dict):
            continue
        out.append(
            {
                "id": str(item.get("id") or f"ai.llm.{i}"),
                "title": str(item.get("title") or "Suggestion"),
                "reason": str(item.get("reason") or ""),
                "score": int(item.get("score") or 50),
                "tourId": item.get("tourId"),
                "href": item.get("href"),
            }
        )
    return out or None
