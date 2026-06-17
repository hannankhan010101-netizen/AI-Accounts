"""Integrations readiness builder."""

from app.core.config import Settings
from app.services.integrations_readiness_service import build_integrations_readiness


def test_fbr_ready_when_enabled_and_credentials_present() -> None:
    settings = Settings(
        fbr_pral_enabled=True,
        fbr_pral_api_url="https://pral.example",
        fbr_pral_api_key="secret",
    )
    out = build_integrations_readiness(settings, fbr_error_count=2, fbr_due_retry_count=1)
    assert out["fbr"]["ready"] is True
    assert out["fbr"]["mode"] == "live"
    assert out["fbr"]["errorCount"] == 2
    assert out["paypro"]["ready"] is False
    assert out["paypro"]["mode"] == "off"


def test_fbr_stub_mode_when_not_configured() -> None:
    settings = Settings(fbr_pral_enabled=False)
    out = build_integrations_readiness(settings)
    assert out["fbr"]["ready"] is False
    assert out["fbr"]["mode"] == "off"
    assert out["fbr"]["stubAvailable"] is True


def test_fbr_stub_mode_when_enabled_but_missing_keys() -> None:
    settings = Settings(fbr_pral_enabled=True, fbr_pral_api_url="", fbr_pral_api_key="")
    out = build_integrations_readiness(settings)
    assert out["fbr"]["mode"] == "stub"
    assert "FBR_PRAL_API_URL" in out["fbr"]["missingEnvKeys"]


def test_paypro_requires_webhook_secret() -> None:
    settings = Settings(
        paypro_enabled=True,
        paypro_merchant_id="m1",
        paypro_api_url="https://pay.example",
        paypro_api_key="k1",
        paypro_webhook_secret="wh",
    )
    out = build_integrations_readiness(settings)
    assert out["paypro"]["ready"] is True
    assert out["paypro"]["mode"] == "live"
