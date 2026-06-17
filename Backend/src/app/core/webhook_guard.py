"""Webhook source IP allowlist — P8."""

from __future__ import annotations

from fastapi import Request

from app.core.config import get_settings


def _parse_allowlist(raw: str) -> set[str]:
    return {ip.strip() for ip in raw.split(",") if ip.strip()}


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return ""


def assert_webhook_ip_allowed(*, request: Request, provider: str) -> None:
    """Raise PermissionError when IP is not on the provider allowlist."""

    settings = get_settings()
    if provider == "paypro":
        raw = (settings.paypro_webhook_allowed_ips or "").strip()
    elif provider == "kuickpay":
        raw = (settings.kuickpay_webhook_allowed_ips or "").strip()
    else:
        raw = ""

    if not raw:
        return

    allowed = _parse_allowlist(raw)
    ip = client_ip(request)
    if ip not in allowed:
        raise PermissionError(f"Webhook IP {ip!r} is not allowed for {provider}")
