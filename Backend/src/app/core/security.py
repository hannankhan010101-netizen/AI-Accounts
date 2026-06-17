"""Password hashing and JWT helpers."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Hash a password for storage."""

    return _pwd.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify password against stored hash."""

    return _pwd.verify(plain_password, password_hash)


def create_access_token(*, subject: str, extra_claims: dict[str, Any]) -> str:
    """Build a signed JWT access token."""

    settings = get_settings()
    expire = datetime.now(tz=UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict[str, Any] = {"sub": subject, "exp": expire, **extra_claims}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(*, subject: str) -> str:
    """Build a signed refresh token (opaque to client structure)."""

    settings = get_settings()
    expire = datetime.now(tz=UTC) + timedelta(days=settings.refresh_token_expire_days)
    payload: dict[str, Any] = {"sub": subject, "typ": "refresh", "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """Decode JWT or raise JWTError."""

    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])


def decode_refresh_token(token: str) -> dict[str, Any]:
    """Decode a refresh JWT and ensure it was minted as ``typ=refresh``."""

    payload = decode_token(token)
    if payload.get("typ") != "refresh":
        raise JWTError("Token is not a refresh token")
    return payload
