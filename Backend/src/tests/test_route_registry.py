"""Ensure critical API paths from the contract are registered on the app."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

from app.main import app


def test_openapi_paths_include_auth_and_bank_payment_post() -> None:
    """Auth lifecycle and tenant bank POST must exist (no 404 from missing route)."""

    paths = app.openapi()["paths"]
    assert "/api/v1/auth/sign-up" in paths and "post" in paths["/api/v1/auth/sign-up"]
    assert "/api/v1/auth/verify-email" in paths and "post" in paths["/api/v1/auth/verify-email"]
    assert "/api/v1/auth/resend-otp" in paths and "post" in paths["/api/v1/auth/resend-otp"]
    assert "/api/v1/auth/forgot-password" in paths and "post" in paths["/api/v1/auth/forgot-password"]
    assert "/api/v1/auth/reset-password" in paths and "post" in paths["/api/v1/auth/reset-password"]
    assert "/api/v1/auth/login" in paths and "post" in paths["/api/v1/auth/login"]
    assert "/api/v1/auth/refresh" in paths and "post" in paths["/api/v1/auth/refresh"]
    assert "/api/v1/auth/logout" in paths and "post" in paths["/api/v1/auth/logout"]
    bank = "/api/v1/companies/{company_id}/bank-payments"
    assert bank in paths
    assert "get" in paths[bank] and "post" in paths[bank]
