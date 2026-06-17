"""Groq SDK wrapper — streaming chat completions with retries."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from typing import Any

from groq import AsyncGroq
from groq.types.chat import ChatCompletionMessageParam

from app.core.config import get_settings
from app.integrations.groq_errors import format_stream_error

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_STATUS = {429, 500, 502, 503, 504}


class GroqClient:
    """Thin async wrapper around Groq chat completions."""

    def __init__(self) -> None:
        settings = get_settings()
        self._enabled = settings.groq_enabled and bool(settings.groq_api_key.strip())
        self._model = settings.groq_model
        self._max_tokens = settings.groq_max_tokens
        self._timeout = settings.groq_timeout_seconds
        self._client: AsyncGroq | None = None
        if self._enabled:
            self._client = AsyncGroq(api_key=settings.groq_api_key, timeout=self._timeout)

    @property
    def enabled(self) -> bool:
        return self._enabled and self._client is not None

    async def chat_completion(
        self,
        *,
        messages: list[ChatCompletionMessageParam],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.3,
    ) -> tuple[str, list[dict[str, Any]]]:
        """Non-streaming completion; returns (content, tool_calls)."""

        if not self._client:
            raise RuntimeError("Groq is not configured")

        kwargs: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": self._max_tokens,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        last_err: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                res = await self._client.chat.completions.create(**kwargs)
                choice = res.choices[0] if res.choices else None
                if not choice or not choice.message:
                    return "", []
                msg = choice.message
                content = (msg.content or "").strip()
                tool_calls: list[dict[str, Any]] = []
                if msg.tool_calls:
                    for tc in msg.tool_calls:
                        fn = tc.function
                        args: dict[str, Any] = {}
                        if fn.arguments:
                            try:
                                args = json.loads(fn.arguments)
                            except json.JSONDecodeError:
                                args = {"raw": fn.arguments}
                        tool_calls.append(
                            {
                                "id": tc.id,
                                "name": fn.name,
                                "arguments": args,
                            }
                        )
                return content, tool_calls
            except Exception as exc:
                last_err = exc
                status = getattr(exc, "status_code", None)
                if status not in RETRY_STATUS and attempt < MAX_RETRIES - 1:
                    if "429" not in str(exc) and "503" not in str(exc):
                        break
                await asyncio.sleep(0.5 * (attempt + 1))
                logger.warning("Groq retry %s: %s", attempt + 1, exc)

        raise last_err or RuntimeError("Groq request failed")

    async def stream_chat(
        self,
        *,
        messages: list[ChatCompletionMessageParam],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.3,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Yield stream events:
        ``{"type": "token", "content": "..."}``,
        ``{"type": "tool_calls", "tool_calls": [...]}``,
        ``{"type": "done"}``.
        """

        if not self._client:
            raise RuntimeError("Groq is not configured")

        kwargs: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": self._max_tokens,
            "stream": True,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        last_err: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                stream = await self._client.chat.completions.create(**kwargs)
                tool_acc: dict[int, dict[str, Any]] = {}
                async for chunk in stream:
                    if not chunk.choices:
                        continue
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield {"type": "token", "content": delta.content}
                    if delta.tool_calls:
                        for tc in delta.tool_calls:
                            idx = tc.index
                            if idx not in tool_acc:
                                tool_acc[idx] = {
                                    "id": tc.id or "",
                                    "name": "",
                                    "arguments": "",
                                }
                            if tc.id:
                                tool_acc[idx]["id"] = tc.id
                            if tc.function:
                                if tc.function.name:
                                    tool_acc[idx]["name"] = tc.function.name
                                if tc.function.arguments:
                                    tool_acc[idx]["arguments"] += tc.function.arguments
                if tool_acc:
                    parsed: list[dict[str, Any]] = []
                    for _idx in sorted(tool_acc.keys()):
                        entry = tool_acc[_idx]
                        args: dict[str, Any] = {}
                        raw = entry.get("arguments") or ""
                        if raw:
                            try:
                                args = json.loads(raw)
                            except json.JSONDecodeError:
                                args = {"raw": raw}
                        parsed.append(
                            {
                                "id": entry["id"],
                                "name": entry["name"],
                                "arguments": args,
                            }
                        )
                    yield {"type": "tool_calls", "tool_calls": parsed}
                yield {"type": "done"}
                return
            except Exception as exc:
                last_err = exc
                await asyncio.sleep(0.5 * (attempt + 1))
                logger.warning("Groq stream retry %s: %s", attempt + 1, exc)

        if last_err:
            yield format_stream_error(last_err)
        else:
            yield {"type": "error", "code": "GROQ_ERROR", "message": "Groq stream failed", "retryable": False}
