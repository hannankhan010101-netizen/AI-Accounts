"""IP allowlist enforcement for tenant memberships."""

import pytest
from fastapi import Request

from app.core.exceptions import ForbiddenError
from app.core.ip_allowlist import assert_membership_ip_allowed


def _request(*, ip: str = "203.0.113.10") -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [],
        "client": (ip, 12345),
    }
    return Request(scope)


def test_empty_allowlist_allows_any_ip() -> None:
    assert_membership_ip_allowed(request=_request(), allowlist_raw=None)
    assert_membership_ip_allowed(request=_request(), allowlist_raw="")


def test_allowlist_blocks_unknown_ip() -> None:
    with pytest.raises(ForbiddenError):
        assert_membership_ip_allowed(
            request=_request(ip="198.51.100.1"),
            allowlist_raw="203.0.113.10, 203.0.113.11",
        )


def test_allowlist_allows_listed_ip() -> None:
    assert_membership_ip_allowed(
        request=_request(ip="203.0.113.11"),
        allowlist_raw="203.0.113.10,203.0.113.11",
    )
