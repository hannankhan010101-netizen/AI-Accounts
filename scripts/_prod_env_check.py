#!/usr/bin/env python3
"""Validate API environment before production deploy (no database required).

Reads Backend/.env by default. For production values without touching dev .env:
  copy Backend/.env.production.example to Backend/.env.production.local (gitignored)
  python scripts/_prod_env_check.py --strict --env-file Backend/.env.production.local

Or set PROD_ENV_FILE. Railway/Vercel inject process env directly (no file needed).

Usage:
  python scripts/_prod_env_check.py
  python scripts/_prod_env_check.py --strict
  python scripts/_prod_env_check.py --strict --env-file Backend/.env.production.local
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BACKEND_ENV = REPO / "Backend" / ".env"
DEFAULT_PROD_LOCAL = REPO / "Backend" / ".env.production.local"

DEV_JWT_MARKERS = (
    "dev-secret",
    "change-me",
    "change_me",
    "min-32-characters-long",
)

LOCALHOST_ORIGIN = re.compile(r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$", re.I)


def _parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def _load_env(*, env_file: str, override: bool) -> str:
    """Load env from file; return source label for output."""

    path: Path | None = None
    if env_file.strip():
        path = Path(env_file.strip())
    elif os.getenv("PROD_ENV_FILE", "").strip():
        path = Path(os.environ["PROD_ENV_FILE"].strip())
    elif DEFAULT_PROD_LOCAL.is_file():
        path = DEFAULT_PROD_LOCAL
    elif BACKEND_ENV.is_file():
        path = BACKEND_ENV

    if path is None or not path.is_file():
        return "process environment"

    try:
        from dotenv import load_dotenv

        load_dotenv(path, override=override)
    except ImportError:
        values = _parse_env_file(path)
        for key, value in values.items():
            if override:
                os.environ[key] = value
            else:
                os.environ.setdefault(key, value)

    return str(path)


def _truthy(name: str, default: str = "") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "on")


def _check(*, strict: bool, source: str) -> int:
    errors: list[str] = []
    warnings: list[str] = []

    jwt = os.getenv("JWT_SECRET_KEY", "").strip()
    if len(jwt) < 32:
        errors.append("JWT_SECRET_KEY must be at least 32 characters")
    elif any(m in jwt.lower() for m in DEV_JWT_MARKERS):
        errors.append("JWT_SECRET_KEY looks like a dev default - rotate before prod")

    if _truthy("AUTH_EXPOSE_OTP_IN_RESPONSE"):
        errors.append("AUTH_EXPOSE_OTP_IN_RESPONSE must be false in production")

    db_url = os.getenv("DATABASE_URL", "").strip()
    if not db_url:
        errors.append("DATABASE_URL is not set")
    elif ":6543" in db_url and "pgbouncer=true" not in db_url:
        warnings.append("DATABASE_URL uses :6543 but missing pgbouncer=true (Supabase transaction pooler)")

    if not os.getenv("DIRECT_URL", "").strip():
        warnings.append("DIRECT_URL not set - Railway release migrations may hang on :6543 pooler")

    cors = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
    if not cors:
        errors.append("CORS_ORIGINS is empty")
    elif all(LOCALHOST_ORIGIN.match(o) for o in cors):
        warnings.append("CORS_ORIGINS is localhost-only - set your public frontend URL")

    app_url = os.getenv("APP_PUBLIC_URL", "").strip()
    if not app_url:
        warnings.append("APP_PUBLIC_URL not set - password-reset and invite links may break")
    elif app_url.startswith("http://") and "localhost" not in app_url:
        warnings.append("APP_PUBLIC_URL should use https in production")

    if not os.getenv("BREVO_API_KEY", "").strip():
        warnings.append("BREVO_API_KEY not set - OTP / password-reset email will fail")
    if not os.getenv("BREVO_SENDER_EMAIL", "").strip():
        warnings.append("BREVO_SENDER_EMAIL not set")

    if os.getenv("OUTBOX_POLL_ENABLED", "1").strip() == "0":
        warnings.append("OUTBOX_POLL_ENABLED=0 - import jobs and async reports will not process")

    if _truthy("FBR_PRAL_ENABLED"):
        if not os.getenv("FBR_PRAL_API_URL", "").strip() or not os.getenv("FBR_PRAL_API_KEY", "").strip():
            errors.append("FBR_PRAL_ENABLED but FBR_PRAL_API_URL / FBR_PRAL_API_KEY missing")

    if _truthy("PAYPRO_ENABLED"):
        required = ("PAYPRO_MERCHANT_ID", "PAYPRO_API_URL", "PAYPRO_API_KEY", "PAYPRO_WEBHOOK_SECRET")
        missing = [k for k in required if not os.getenv(k, "").strip()]
        if missing:
            errors.append(f"PAYPRO_ENABLED but missing: {', '.join(missing)}")

    print("=== Production env check (API) ===\n")
    print(f"  Source: {source}")
    print(f"  DATABASE_URL:     {'set' if db_url else 'MISSING'}")
    print(f"  DIRECT_URL:       {'set' if os.getenv('DIRECT_URL') else 'missing'}")
    print(f"  JWT_SECRET_KEY:   {'set (' + str(len(jwt)) + ' chars)' if jwt else 'MISSING'}")
    print(f"  CORS_ORIGINS:     {', '.join(cors) if cors else '(empty)'}")
    print(f"  APP_PUBLIC_URL:   {app_url or '(missing)'}")
    print(f"  BREVO:            {'configured' if os.getenv('BREVO_API_KEY') else 'not configured'}")
    print(f"  OUTBOX_POLL:      {os.getenv('OUTBOX_POLL_ENABLED', '1')}")

    if warnings:
        print("\n  Warnings:")
        for w in warnings:
            print(f"    - {w}")

    if errors:
        print("\n  ERRORS:")
        for e in errors:
            print(f"    - {e}")
        print("\n  ENV CHECK: FAIL")
        return 1

    if strict and warnings:
        print("\n  ENV CHECK: FAIL (--strict: resolve warnings before prod)")
        return 1

    print("\n  ENV CHECK: PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Production API environment validation")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors (recommended before go-live deploy)",
    )
    parser.add_argument(
        "--env-file",
        default="",
        help="Env file to validate (default: PROD_ENV_FILE, .env.production.local, or Backend/.env)",
    )
    args = parser.parse_args()
    explicit = bool(args.env_file.strip() or os.getenv("PROD_ENV_FILE", "").strip())
    source = _load_env(env_file=args.env_file, override=explicit or DEFAULT_PROD_LOCAL.is_file())
    return _check(strict=args.strict, source=source)


if __name__ == "__main__":
    raise SystemExit(main())
