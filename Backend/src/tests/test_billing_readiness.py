"""Billing readiness builder."""

from app.core.config import Settings
from app.services.billing_readiness_service import build_billing_readiness


def test_billing_live_when_all_stripe_env_present() -> None:
    settings = Settings(
        stripe_secret_key="sk_test",
        stripe_price_starter="price_starter",
        stripe_price_pro="price_pro",
        stripe_webhook_secret="whsec",
    )
    out = build_billing_readiness(settings)
    assert out["ready"] is True
    assert out["mode"] == "live"
    assert out["missingEnvKeys"] == []


def test_billing_stub_when_secret_missing() -> None:
    settings = Settings()
    out = build_billing_readiness(settings)
    assert out["ready"] is False
    assert out["stubAvailable"] is True
    assert "STRIPE_SECRET_KEY" in out["missingEnvKeys"]
