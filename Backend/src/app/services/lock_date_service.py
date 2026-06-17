"""Lock date enforcement — catalog §3.14, §9.5.

Every route that creates or edits a transaction with a business date must
call ``assert_not_locked`` to prevent backdated changes before the company
lock date. Per-user lock-date extension lands in Phase 1.6b; for now we only
enforce the global setting.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.core.exceptions import ValidationAppError
from app.core.tenant_context import get_current_user_id
from app.repositories.lock_date_repository import LockDateRepository


class LockDateService:
    """Validates document dates against the company's lock-date policy."""

    def __init__(self, lock_date_repository: LockDateRepository) -> None:
        self._repo = lock_date_repository

    async def assert_not_locked(
        self,
        *,
        company_id: str,
        document_date: datetime,
        document_label: str = "document",
        user_id: str | None = None,
    ) -> None:
        """
        Raise ``ValidationAppError`` when ``document_date`` is on or before
        the effective lock date.

        Per-user extensions (P4): when a user has an earlier ``extendedLockDate``
        than the company global lock, they may post in the gap period.
        """

        row = await self._repo.get_for_company(company_id=company_id)
        if row is None or row.globalLockDate is None:
            return

        doc = _to_utc(document_date)
        lock = _to_utc(row.globalLockDate)
        effective_user = user_id or get_current_user_id()
        if effective_user:
            extended = await self._repo.get_user_extension(
                company_id=company_id, user_id=effective_user
            )
            if extended is not None:
                ext = _to_utc(extended)
                if ext < lock:
                    lock = ext
        if doc <= lock:
            raise ValidationAppError(
                f"{document_label.capitalize()} date {doc.date().isoformat()} is on or "
                f"before the lock date {lock.date().isoformat()}."
            )

    async def set_user_extension(
        self,
        *,
        company_id: str,
        user_id: str,
        extended_lock_date: datetime,
    ) -> None:
        await self._repo.upsert_user_extension(
            company_id=company_id,
            user_id=user_id,
            extended_lock_date=extended_lock_date,
        )


def _to_utc(value: Any) -> datetime:
    """Normalize to a timezone-aware UTC datetime."""

    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    return datetime.fromisoformat(str(value)).astimezone(timezone.utc)
