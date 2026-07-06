"""Build system prompts from route, permissions, and assistant mode."""

from __future__ import annotations

import json
from typing import Any


def infer_mode(pathname: str, explicit: str | None = None) -> str:
    if explicit and explicit != "default":
        return explicit
    p = pathname or "/"
    if "/sales/invoices" in p:
        return "invoice"
    if "/bank" in p and "recon" in p:
        return "reconciliation"
    if "/inventory" in p:
        return "inventory"
    if "/reports" in p:
        return "reports"
    if "/settings" in p and ("audit" in p or "user-log" in p):
        return "audit"
    if "/onboarding" in p or "/learning" in p:
        return "onboarding"
    return "erp_help"


def build_system_prompt(
    *,
    mode: str,
    pathname: str,
    permissions: list[str],
    locale: str | None,
    screen_context: dict[str, Any] | None,
    onboarding_progress: dict[str, Any] | None,
) -> str:
    perms_snip = permissions[:40]
    ctx = {
        "pathname": pathname,
        "mode": mode,
        "permissions": perms_snip,
        "screen": screen_context or {},
    }
    if onboarding_progress and mode == "onboarding":
        ctx["onboarding"] = {
            "maturityScore": onboarding_progress.get("maturityScore", 0),
            "completedTours": [
                k
                for k, v in (onboarding_progress.get("tours") or {}).items()
                if isinstance(v, dict) and v.get("status") == "completed"
            ],
        }

    # Prompt text is centralized in the versioned registry (services/ai/prompts).
    from app.services.ai.prompts.prompt_registry import (
        LOCALE_HINT_TEMPLATE,
        get_prompt,
        mode_hint,
    )

    locale_hint = LOCALE_HINT_TEMPLATE.format(locale=locale) if locale else ""
    base = get_prompt("assistant.system.base").render(
        locale_hint=locale_hint,
        context_json=json.dumps(ctx, default=str)[:4000],
    )
    return base + mode_hint(mode)
