"""Map Groq API failures to assistant SSE error payloads."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

TOOL_GENERATION_MARKERS = (
    "failed to call a function",
    "failed_generation",
    "tool_use_failed",
    "invalid tool",
)


def is_tool_generation_failure(message: str) -> bool:
    lower = (message or "").lower()
    return any(marker in lower for marker in TOOL_GENERATION_MARKERS)


def _extract_failed_generation(exc: Exception) -> str | None:
    body = getattr(exc, "body", None)
    if isinstance(body, dict):
        err = body.get("error")
        if isinstance(err, dict):
            fg = err.get("failed_generation")
            if isinstance(fg, str) and fg.strip():
                return fg.strip()
    return None


def format_stream_error(exc: Exception) -> dict[str, Any]:
    """Build a client-safe SSE error event."""

    raw = str(exc).strip() or "AI request failed"
    failed_gen = _extract_failed_generation(exc)
    if failed_gen:
        logger.warning("Groq failed_generation: %s", failed_gen[:500])

    if is_tool_generation_failure(raw) or failed_gen:
        return {
            "type": "error",
            "code": "GROQ_TOOL_FAILED",
            "message": (
                "I could not run an automated action for that question. "
                "I'll answer in plain language — try sending again or rephrase your question."
            ),
            "retryable": True,
        }

    if "429" in raw or "rate" in raw.lower():
        return {
            "type": "error",
            "code": "RATE_LIMIT",
            "message": "Too many AI requests. Please wait a moment and try again.",
            "retryable": True,
        }

    return {
        "type": "error",
        "code": "GROQ_ERROR",
        "message": raw,
        "retryable": False,
    }
