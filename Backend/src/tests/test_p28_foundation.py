"""P28 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.constants import auth_purposes as otp_purpose
from app.constants.permission_catalog import flatten_permission_entries
from app.services.permission_validation_service import known_permission_codes


def test_settings_users_invite_in_catalog() -> None:
    codes = known_permission_codes()
    assert "settings.users.invite" in codes


def test_user_invite_purpose_constant() -> None:
    assert otp_purpose.USER_INVITE == "user_invite"


@pytest.mark.asyncio
async def test_openapi_p28_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/auth/accept-invite" in paths
    assert "/api/v1/companies/{company_id}/roles/{role_id}/clone" in paths
    tree_codes = {p["code"] for p in flatten_permission_entries()}
    assert "settings.users.invite" in tree_codes
