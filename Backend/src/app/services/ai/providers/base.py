"""Provider contract + pure format converters (no SDK imports here).

The converters are deliberately dependency-free so they can be unit-tested in the
provider-conformance suite without any LLM SDK installed or network access.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any, Literal, Protocol, runtime_checkable

ProviderName = Literal["groq", "claude", "openai"]

# Task tiers → routing. "deep" = quality-sensitive reasoning/insights (Sonnet-class);
# "fast" = high-volume inline suggestions/autocomplete (Haiku/Groq-class).
TaskTier = Literal["deep", "fast"]


@runtime_checkable
class LLMProvider(Protocol):
    """Structural contract every adapter satisfies (GroqClient already does)."""

    @property
    def enabled(self) -> bool: ...

    def stream_chat(
        self,
        *,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.3,
    ) -> AsyncIterator[dict[str, Any]]: ...

    async def chat_completion(
        self,
        *,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.3,
    ) -> tuple[str, list[dict[str, Any]]]: ...


# ---------------------------------------------------------------------------
# OpenAI/Groq  ->  Anthropic conversion (pure functions)
# ---------------------------------------------------------------------------

def split_system_and_messages(
    messages: list[dict[str, Any]],
) -> tuple[str, list[dict[str, Any]]]:
    """Return (system_prompt, anthropic_messages).

    Input is the OpenAI/Groq message list the orchestrator builds:
      - {"role":"system","content":str}
      - {"role":"user","content":str}
      - {"role":"assistant","content":str|None,"tool_calls":[{id,function:{name,arguments}}]}
      - {"role":"tool","tool_call_id":str,"content":str}

    Anthropic wants the system prompt out-of-band, ``tool_use`` blocks on assistant
    turns, ``tool_result`` blocks on user turns, and no two consecutive same-role
    messages — so tool results are merged into a single user turn.
    """

    system_parts: list[str] = []
    converted: list[dict[str, Any]] = []

    for msg in messages:
        role = msg.get("role")
        if role == "system":
            content = msg.get("content")
            if content:
                system_parts.append(str(content))
            continue

        if role == "tool":
            block = {
                "type": "tool_result",
                "tool_use_id": msg.get("tool_call_id") or "",
                "content": str(msg.get("content") or ""),
            }
            _append_or_merge(converted, "user", [block])
            continue

        if role == "assistant":
            blocks: list[dict[str, Any]] = []
            text = msg.get("content")
            if text:
                blocks.append({"type": "text", "text": str(text)})
            for tc in msg.get("tool_calls") or []:
                fn = tc.get("function") or {}
                raw_args = fn.get("arguments")
                if isinstance(raw_args, str):
                    try:
                        parsed_args = json.loads(raw_args) if raw_args else {}
                    except json.JSONDecodeError:
                        parsed_args = {}
                else:
                    parsed_args = raw_args or {}
                blocks.append(
                    {
                        "type": "tool_use",
                        "id": tc.get("id") or "",
                        "name": fn.get("name") or "",
                        "input": parsed_args,
                    }
                )
            if not blocks:
                blocks = [{"type": "text", "text": ""}]
            _append_or_merge(converted, "assistant", blocks)
            continue

        # default: user
        content = msg.get("content")
        _append_or_merge(
            converted, "user", [{"type": "text", "text": str(content or "")}]
        )

    return "\n\n".join(system_parts).strip(), converted


def _append_or_merge(
    acc: list[dict[str, Any]], role: str, blocks: list[dict[str, Any]]
) -> None:
    """Anthropic rejects consecutive same-role turns — merge their content blocks."""

    if acc and acc[-1]["role"] == role:
        acc[-1]["content"].extend(blocks)
    else:
        acc.append({"role": role, "content": list(blocks)})


def openai_tools_to_anthropic(
    tools: list[dict[str, Any]] | None,
) -> list[dict[str, Any]] | None:
    """{"type":"function","function":{name,description,parameters}} -> {name,description,input_schema}."""

    if not tools:
        return None
    out: list[dict[str, Any]] = []
    for tool in tools:
        fn = tool.get("function") or {}
        name = fn.get("name")
        if not name:
            continue
        out.append(
            {
                "name": name,
                "description": fn.get("description") or "",
                "input_schema": fn.get("parameters")
                or {"type": "object", "properties": {}},
            }
        )
    return out or None
