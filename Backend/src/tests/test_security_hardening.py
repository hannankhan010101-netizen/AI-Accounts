"""Phase-0 security hardening regression tests (no DB required)."""

from __future__ import annotations

import pytest

from app.services.attachment_storage import (
    UnsafeStorageKeyError,
    assert_safe_storage_key,
    resolve_path,
)

_ATTACKS = [
    "../../../../etc/passwd",
    "..\\..\\..\\windows\\win.ini",
    "/etc/shadow",
    "C:/Windows/System32/drivers/etc/hosts",
    "companyA/../../etc/passwd",
    "./../x",
    "",
]


@pytest.mark.parametrize("attack", _ATTACKS)
def test_attachment_path_traversal_blocked(attack):
    with pytest.raises((UnsafeStorageKeyError, FileNotFoundError)):
        resolve_path(attack, company_id="companyA")


def test_attachment_cross_tenant_key_rejected_at_register():
    # a member of companyA cannot register another tenant's blob key
    with pytest.raises(UnsafeStorageKeyError):
        assert_safe_storage_key("otherCompany/blob", company_id="companyA")


def test_attachment_legit_key_allowed():
    key = assert_safe_storage_key("companyA/deadbeef_file.png", company_id="companyA")
    assert key == "companyA/deadbeef_file.png"
    p = resolve_path("companyA/deadbeef_file.png", company_id="companyA")
    assert "companyA" in str(p)


def test_uploads_root_containment_without_company_scope():
    # even with no company scope, keys must never escape the uploads root
    with pytest.raises((UnsafeStorageKeyError, FileNotFoundError)):
        resolve_path("../../../../etc/passwd")


def test_login_rejects_inactive_user():
    """login() must reject a deactivated user (same failure as bad password)."""

    import asyncio
    from unittest.mock import AsyncMock

    from app.core.exceptions import UnauthorizedError
    from app.services.auth_service import AuthService

    # Build an AuthService with only the collaborators login() touches.
    svc = AuthService.__new__(AuthService)
    svc._users = AsyncMock()
    svc._companies = AsyncMock()

    class _User:
        id = "u1"
        passwordHash = "hash"
        emailVerified = True
        isActive = False

    svc._users.find_by_email.return_value = _User()

    class _Req:
        email = "x@example.com"
        password = "pw"

    # verify_password is imported into the module namespace; force it True so only
    # the isActive gate can fail.
    import app.services.auth_service as auth_mod

    orig = auth_mod.verify_password
    auth_mod.verify_password = lambda *a, **k: True
    try:
        with pytest.raises(UnauthorizedError):
            asyncio.run(svc.login(request=_Req()))
    finally:
        auth_mod.verify_password = orig
