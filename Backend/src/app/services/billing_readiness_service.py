"""Billing / Stripe readiness flags (no secrets) — P9."""

from __future__ import annotations

from typing import Any

from app.core.config import Settings


def build_billing_readiness(settings: Settings) -> dict[str, Any]:
    """Summarize whether Stripe checkout/portal can run in live mode."""

    secret = (settings.stripe_secret_key or "").strip()
    starter_price = (settings.stripe_price_starter or "").strip()
    pro_price = (settings.stripe_price_pro or "").strip()
    webhook = (settings.stripe_webhook_secret or "").strip()

    missing: list[str] = []
    if not secret:
        missing.append("STRIPE_SECRET_KEY")
    if not starter_price:
        missing.append("STRIPE_PRICE_STARTER")
    if not pro_price:
        missing.append("STRIPE_PRICE_PRO")
    if not webhook:
        missing.append("STRIPE_WEBHOOK_SECRET")

    configured = not missing
    mode = "live" if configured else ("stub" if secret else "stub")
    return {
        "configured": configured,
        "ready": configured,
        "mode": mode,
        "missingEnvKeys": missing,
        "stubAvailable": True,
    }
