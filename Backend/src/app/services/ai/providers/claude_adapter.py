"""Anthropic Claude adapter — primary provider for reasoning/insights.

Emits the same event dicts as GroqClient so the orchestrator stays provider-blind.
The ``anthropic`` SDK is imported lazily; if it is missing or unconfigured the
adapter reports ``enabled == False`` and callers degrade gracefully (same idiom
the codebase uses for redis/fpdf2).
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from typing import Any

from app.core.config import get_settings
from app.integrations.groq_errors import format_stream_error  # legacy-named codes; client-stable
from app.services.ai.providers.base import (
    openai_tools_to_anthropic,
    split_system_and_messages,
)

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_STATUS = {429, 500, 502, 503, 504}


class ClaudeProvider:
    """Async wrapper around Anthropic Messages API in the shared event contract."""

    name = "claude"

    def __init__(self) -> None:
        settings = get_settings()
        self._model = settings.anthropic_model
        self._max_tokens = settings.anthropic_max_tokens
        self._timeout = settings.anthropic_timeout_seconds
        self._client: Any | None = None
        key = (settings.anthropic_api_key or "").strip()
        self._enabled = bool(settings.anthropic_enabled and key)
        if self._enabled:
            try:
                from anthropic import AsyncAnthropic

                self._client = AsyncAnthropic(api_key=key, timeout=self._timeout)
            except Exception as exc:  # SDK missing / bad config → degrade, don't crash import
                logger.warning("Claude provider unavailable: %s", exc)
                self._enabled = False

    @property
    def enabled(self) -> bool:
        return self._enabled and self._client is not None

    def _kwargs(
        self,
        *,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None,
        temperature: float,
    ) -> dict[str, Any]:
        system, anthropic_messages = split_system_and_messages(messages)
        kwargs: dict[str, Any] = {
            "model": self._model,
            "max_tokens": self._max_tokens,
            "temperature": temperature,
            "messages": anthropic_messages,
        }
        if system:
            kwargs["system"] = system
        anthropic_tools = openai_tools_to_anthropic(tools)
        if anthropic_tools:
            kwargs["tools"] = anthropic_tools
        return kwargs

    async def chat_completion(
        self,
        *,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.3,
    ) -> tuple[str, list[dict[str, Any]]]:
        if not self._client:
            raise RuntimeError("Claude is not configured")
        kwargs = self._kwargs(messages=messages, tools=tools, temperature=temperature)

        last_err: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                res = await self._client.messages.create(**kwargs)
                text_parts: list[str] = []
                tool_calls: list[dict[str, Any]] = []
                for block in getattr(res, "content", []) or []:
                    btype = getattr(block, "type", None)
                    if btype == "text":
                        text_parts.append(getattr(block, "text", "") or "")
                    elif btype == "tool_use":
                        tool_calls.append(
                            {
                                "id": getattr(block, "id", "") or "",
                                "name": getattr(block, "name", "") or "",
                                "arguments": getattr(block, "input", {}) or {},
                            }
                        )
                return "".join(text_parts).strip(), tool_calls
            except Exception as exc:
                last_err = exc
                status = getattr(exc, "status_code", None)
                if status not in RETRY_STATUS and attempt < MAX_RETRIES - 1:
                    if "429" not in str(exc) and "503" not in str(exc):
                        break
                await asyncio.sleep(0.5 * (attempt + 1))
                logger.warning("Claude retry %s: %s", attempt + 1, exc)

        raise last_err or RuntimeError("Claude request failed")

    async def stream_chat(
        self,
        *,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.3,
    ) -> AsyncIterator[dict[str, Any]]:
        if not self._client:
            raise RuntimeError("Claude is not configured")
        kwargs = self._kwargs(messages=messages, tools=tools, temperature=temperature)

        last_err: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                tool_acc: dict[int, dict[str, Any]] = {}
                async with self._client.messages.stream(**kwargs) as stream:
                    async for event in stream:
                        etype = getattr(event, "type", None)
                        if etype == "content_block_start":
                            block = getattr(event, "content_block", None)
                            if getattr(block, "type", None) == "tool_use":
                                tool_acc[getattr(event, "index", 0)] = {
                                    "id": getattr(block, "id", "") or "",
                                    "name": getattr(block, "name", "") or "",
                                    "arguments": "",
                                }
                        elif etype == "content_block_delta":
                            delta = getattr(event, "delta", None)
                            dtype = getattr(delta, "type", None)
                            if dtype == "text_delta":
                                text = getattr(delta, "text", "") or ""
                                if text:
                                    yield {"type": "token", "content": text}
                            elif dtype == "input_json_delta":
                                idx = getattr(event, "index", 0)
                                if idx in tool_acc:
                                    tool_acc[idx]["arguments"] += (
                                        getattr(delta, "partial_json", "") or ""
                                    )
                if tool_acc:
                    yield {"type": "tool_calls", "tool_calls": _finalize_tools(tool_acc)}
                yield {"type": "done"}
                return
            except Exception as exc:
                last_err = exc
                await asyncio.sleep(0.5 * (attempt + 1))
                logger.warning("Claude stream retry %s: %s", attempt + 1, exc)

        yield format_stream_error(last_err or RuntimeError("Claude stream failed"))


def _finalize_tools(tool_acc: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    import json

    parsed: list[dict[str, Any]] = []
    for idx in sorted(tool_acc.keys()):
        entry = tool_acc[idx]
        raw = entry.get("arguments") or ""
        try:
            args = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            args = {"raw": raw}
        parsed.append({"id": entry["id"], "name": entry["name"], "arguments": args})
    return parsed
