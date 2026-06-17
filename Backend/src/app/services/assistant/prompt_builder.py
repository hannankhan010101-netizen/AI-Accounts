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

    locale_hint = f"Reply in locale '{locale}' when provided." if locale else ""

    base = (
        "You are the Fast Accounts ERP AI copilot — concise, accurate, and action-oriented. "
        "You help users navigate accounting workflows: sales, purchases, bank, inventory, "
        "reports, and settings. Never invent features outside this product. "
        "Use tools when they help the user complete a task. "
        "For write operations (invoices, payments), explain steps and require user confirmation. "
        "Respect RBAC: if the user lacks permissions, say so and suggest alternatives. "
        f"{locale_hint}\n\n"
        f"Context JSON:\n{json.dumps(ctx, default=str)[:4000]}"
    )

    mode_hints = {
        "onboarding": " Focus on guided tours, learning paths, and next onboarding steps.",
        "invoice": " Focus on sales invoices, customers, and receipts.",
        "reconciliation": " Focus on bank reconciliation and matching transactions.",
        "inventory": " Focus on stock, products, and adjustments.",
        "reports": " Focus on financial reports and how to interpret them.",
        "audit": (
            " Focus on audit log entries and compliance visibility. "
            "Prefer answering in plain language; use explainAuditEntry only when the user "
            "asks for recent log rows or specific transaction types."
        ),
    }
    return base + mode_hints.get(mode, "")
