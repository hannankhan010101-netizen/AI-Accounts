"""LLM provider adapters behind one streaming event-dict contract.

Every provider (Groq, Claude, OpenAI-compatible) exposes the same surface the
assistant orchestrator already depends on:

- ``enabled`` -> bool
- ``stream_chat(*, messages, tools=None, temperature=0.3)`` -> async iterator of
  ``{"type": "token"|"tool_calls"|"done"|"error", ...}`` event dicts
- ``chat_completion(*, messages, tools=None, temperature=0.3)`` -> (content, tool_calls)

``messages``/``tools`` are always in the OpenAI/Groq shape; each non-OpenAI
adapter converts internally so callers never branch on provider.
"""

from __future__ import annotations

from app.services.ai.providers.base import LLMProvider, ProviderName

__all__ = ["LLMProvider", "ProviderName", "get_provider", "get_router"]


def get_provider(name: "ProviderName"):
    """Construct a single provider adapter by name (lazy imports)."""

    if name == "claude":
        from app.services.ai.providers.claude_adapter import ClaudeProvider

        return ClaudeProvider()
    if name == "openai":
        from app.services.ai.providers.openai_adapter import OpenAIProvider

        return OpenAIProvider()
    from app.integrations.groq_client import GroqClient  # groq already satisfies LLMProvider

    return GroqClient()


def get_router():
    """Construct the task-tier ProviderRouter (primary + fallback lane)."""

    from app.services.ai.providers.router import ProviderRouter

    return ProviderRouter()
