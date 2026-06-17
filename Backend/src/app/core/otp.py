"""Email OTP generation and verification (HMAC, no plaintext storage)."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

from app.core.config import get_settings


def generate_six_digit_otp() -> str:
    """Return a 6-digit numeric OTP as a zero-padded string."""

    return f"{secrets.randbelow(1_000_000):06d}"


def hash_otp(*, email: str, purpose: str, code: str) -> str:
    """Derive a stored digest for ``code`` scoped by email and purpose."""

    settings = get_settings()
    key = settings.jwt_secret_key.encode("utf-8")
    msg = f"{purpose}:{email.lower().strip()}:{code}".encode("utf-8")
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


def verify_otp(*, email: str, purpose: str, code: str, code_hash: str) -> bool:
    """Constant-time compare of user input to stored digest."""

    candidate = hash_otp(email=email, purpose=purpose, code=code)
    return hmac.compare_digest(candidate, code_hash)


def otp_expiry(*, ttl_minutes: int) -> datetime:
    """UTC expiry instant for a new challenge."""

    return datetime.now(tz=UTC) + timedelta(minutes=ttl_minutes)
