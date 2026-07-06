"""OpenAI-compatible adapter over httpx (no extra SDK).

Works with OpenAI and any OpenAI-compatible endpoint (the onboarding LLM base_url
is reused as the default). Streaming/tool-call delta shape matches Groq's, so the
same accumulation logic applies. Emits the shared event-dict contract.
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from typing import Any

import httpx

from app.core.config import get_settings
from app.integrations.groq_errors import format_stream_error

logger = logging.getLogger(__name__)

MAX_RETRIES = 3


class OpenAIProvider:
    name = "openai"

    def __init__(self) -> None:
        settings = get_settings()
        self._base_url = (settings.onboarding_llm_base_url or "").rstrip("/")
        self._model = settings.onboarding_llm_model
        self._timeout = max(settings.onboarding_llm_timeout_seconds, 30.0)
        self._max_tokens = settings.groq_max_tokens
        key = (settings.onboarding_llm_api_key or "").strip()
        self._key = key
        self._enabled = bool(settings.onboarding_llm_enabled and key and self._base_url)

    @property
    def enabled(self) -> bool:
        return self._enabled

    def _payload(
        self,
        *,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None,
        temperature: float,
        stream: bool,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": self._max_tokens,
            "stream": stream,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        return payload

    @property
    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._key}", "Content-Type": "application/json"}

    async def chat_completion(
        self,
        *,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.3,
    ) -> tuple[str, list[dict[str, Any]]]:
        if not self._enabled:
            raise RuntimeError("OpenAI provider is not configured")
        payload = self._payload(
            messages=messages, tools=tools, temperature=temperature, stream=False
        )
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            res = await client.post(
                f"{self._base_url}/chat/completions", headers=self._headers, json=payload
            )
            res.raise_for_status()
            data = res.json()
        choice = (data.get("choices") or [{}])[0]
        msg = choice.get("message") or {}
        content = (msg.get("content") or "").strip()
        tool_calls: list[dict[str, Any]] = []
        for tc in msg.get("tool_calls") or []:
            fn = tc.get("function") or {}
            raw = fn.get("arguments") or ""
            try:
                args = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                args = {"raw": raw}
            tool_calls.append({"id": tc.get("id") or "", "name": fn.get("name") or "", "arguments": args})
        return content, tool_calls

    async def stream_chat(
        self,
        *,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.3,
    ) -> AsyncIterator[dict[str, Any]]:
        if not self._enabled:
            raise RuntimeError("OpenAI provider is not configured")
        payload = self._payload(
            messages=messages, tools=tools, temperature=temperature, stream=True
        )

        last_err: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                tool_acc: dict[int, dict[str, Any]] = {}
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    async with client.stream(
                        "POST",
                        f"{self._base_url}/chat/completions",
                        headers=self._headers,
                        json=payload,
                    ) as res:
                        res.raise_for_status()
                        async for line in res.aiter_lines():
                            if not line or not line.startswith("data:"):
                                continue
                            data = line[len("data:") :].strip()
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                            except json.JSONDecodeError:
                                continue
                            delta = ((chunk.get("choices") or [{}])[0]).get("delta") or {}
                            if delta.get("content"):
                                yield {"type": "token", "content": delta["content"]}
                            for tc in delta.get("tool_calls") or []:
                                idx = tc.get("index", 0)
                                acc = tool_acc.setdefault(
                                    idx, {"id": "", "name": "", "arguments": ""}
                                )
                                if tc.get("id"):
                                    acc["id"] = tc["id"]
                                fn = tc.get("function") or {}
                                if fn.get("name"):
                                    acc["name"] = fn["name"]
                                if fn.get("arguments"):
                                    acc["arguments"] += fn["arguments"]
                if tool_acc:
                    parsed: list[dict[str, Any]] = []
                    for idx in sorted(tool_acc.keys()):
                        entry = tool_acc[idx]
                        raw = entry.get("arguments") or ""
                        try:
                            args = json.loads(raw) if raw else {}
                        except json.JSONDecodeError:
                            args = {"raw": raw}
                        parsed.append({"id": entry["id"], "name": entry["name"], "arguments": args})
                    yield {"type": "tool_calls", "tool_calls": parsed}
                yield {"type": "done"}
                return
            except Exception as exc:
                last_err = exc
                await asyncio.sleep(0.5 * (attempt + 1))
                logger.warning("OpenAI stream retry %s: %s", attempt + 1, exc)

        yield format_stream_error(last_err or RuntimeError("OpenAI stream failed"))
