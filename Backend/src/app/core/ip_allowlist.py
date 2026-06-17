"""Per-membership IP allowlist enforcement — P9."""

from __future__ import annotations

from fastapi import Request

from app.core.exceptions import ForbiddenError
from app.core.webhook_guard import _parse_allowlist, client_ip


def assert_membership_ip_allowed(
    *, request: Request, allowlist_raw: str | None
) -> None:
    """Raise ``ForbiddenError`` when the client IP is not on the membership allowlist."""

    raw = (allowlist_raw or "").strip()
    if not raw:
        return
    allowed = _parse_allowlist(raw)
    ip = client_ip(request)
    if ip not in allowed:
        raise ForbiddenError(
            f"Access denied from IP {ip!r}; contact an administrator to update your allowlist"
        )
