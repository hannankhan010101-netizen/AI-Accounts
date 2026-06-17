"""Integration readiness flags (no secrets) for ops dashboards."""

from __future__ import annotations

from typing import Any

from app.core.config import Settings


def _provider_detail(
    *,
    enabled: bool,
    required: list[tuple[str, str]],
) -> dict[str, Any]:
    """Build provider status; required is (settings value, ENV_KEY name) pairs."""

    missing_env_keys = [env_key for value, env_key in required if not str(value or "").strip()]
    configured = enabled and not missing_env_keys
    if not enabled:
        mode = "off"
    elif configured:
        mode = "live"
    else:
        mode = "stub"
    return {
        "enabled": enabled,
        "configured": configured,
        "ready": configured,
        "mode": mode,
        "missingEnvKeys": missing_env_keys,
    }


def build_integrations_readiness(
    settings: Settings,
    *,
    fbr_error_count: int = 0,
    fbr_due_retry_count: int = 0,
) -> dict[str, Any]:
    """Summarize whether prod integrations can be used (env + feature flags)."""

    fbr = _provider_detail(
        enabled=settings.fbr_pral_enabled,
        required=[
            (settings.fbr_pral_api_url, "FBR_PRAL_API_URL"),
            (settings.fbr_pral_api_key, "FBR_PRAL_API_KEY"),
        ],
    )
    fbr["errorCount"] = fbr_error_count
    fbr["dueRetryCount"] = fbr_due_retry_count
    fbr["stubAvailable"] = True
    fbr["retryWorkerEnabled"] = settings.fbr_retry_enabled

    paypro = _provider_detail(
        enabled=settings.paypro_enabled,
        required=[
            (settings.paypro_merchant_id, "PAYPRO_MERCHANT_ID"),
            (settings.paypro_api_url, "PAYPRO_API_URL"),
            (settings.paypro_api_key, "PAYPRO_API_KEY"),
            (settings.paypro_webhook_secret, "PAYPRO_WEBHOOK_SECRET"),
        ],
    )
    paypro["stubAvailable"] = settings.paypro_enabled or bool(settings.paypro_merchant_id)

    kuickpay = _provider_detail(
        enabled=settings.kuickpay_enabled,
        required=[
            (settings.kuickpay_merchant_id, "KUICKPAY_MERCHANT_ID"),
            (settings.kuickpay_api_url, "KUICKPAY_API_URL"),
            (settings.kuickpay_api_key, "KUICKPAY_API_KEY"),
            (settings.kuickpay_webhook_secret, "KUICKPAY_WEBHOOK_SECRET"),
        ],
    )
    kuickpay["stubAvailable"] = settings.kuickpay_enabled or bool(settings.kuickpay_merchant_id)

    return {
        "fbr": fbr,
        "paypro": paypro,
        "kuickpay": kuickpay,
        "fbrRetryWorker": settings.fbr_retry_enabled,
    }
