"""Task-tier provider router.

Chooses a provider per task tier and falls back to whatever is enabled, so the
platform keeps working when only one key is configured (today: Groq-only). It
satisfies the same contract as a single provider, so it drops into the assistant
orchestrator unchanged. Callers may pass an optional ``tier``; conversational use
defaults to ``deep`` (quality-sensitive), inline/high-volume use passes ``fast``.

Mid-stream cross-provider failover is intentionally out of scope for Phase 1
(streaming errors surface as error events); Phase 7 adds it.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from typing import Any

from app.core.config import get_settings
from app.services.ai.providers import get_provider
from app.services.ai.providers.base import LLMProvider, ProviderName, TaskTier

logger = logging.getLogger(__name__)

_ALL: tuple[ProviderName, ...] = ("claude", "groq", "openai")


class ProviderRouter:
    def __init__(self) -> None:
        settings = get_settings()
        self._primary: ProviderName = _coerce(settings.ai_provider_primary, "claude")
        self._fast: ProviderName = _coerce(settings.ai_provider_fast, "groq")
        self._cache: dict[ProviderName, LLMProvider] = {}

    def _get(self, name: ProviderName) -> LLMProvider:
        if name not in self._cache:
            self._cache[name] = get_provider(name)
        return self._cache[name]

    def _order(self, tier: TaskTier) -> list[ProviderName]:
        head = self._fast if tier == "fast" else self._primary
        # preferred provider for the tier first, then the rest as fallback lanes
        return [head, *[n for n in _ALL if n != head]]

    def select(self, tier: TaskTier = "deep") -> LLMProvider | None:
        for name in self._order(tier):
            provider = self._get(name)
            if provider.enabled:
                return provider
        return None

    @property
    def enabled(self) -> bool:
        return any(self._get(n).enabled for n in _ALL)

    async def chat_completion(
        self,
        *,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.3,
        tier: TaskTier = "deep",
    ) -> tuple[str, list[dict[str, Any]]]:
        provider = self.select(tier)
        if provider is None:
            raise RuntimeError("No AI provider is configured")
        return await provider.chat_completion(
            messages=messages, tools=tools, temperature=temperature
        )

    async def stream_chat(
        self,
        *,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.3,
        tier: TaskTier = "deep",
    ) -> AsyncIterator[dict[str, Any]]:
        provider = self.select(tier)
        if provider is None:
            yield {
                "type": "error",
                "code": "GROQ_ERROR",
                "message": "AI assistant is not configured on this server.",
                "retryable": False,
            }
            return
        async for event in provider.stream_chat(
            messages=messages, tools=tools, temperature=temperature
        ):
            yield event


def _coerce(value: str, default: ProviderName) -> ProviderName:
    v = (value or "").strip().lower()
    return v if v in _ALL else default  # type: ignore[return-value]
