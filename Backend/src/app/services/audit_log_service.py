"""User log read path and append helper for mutations."""

from __future__ import annotations

from datetime import datetime

from app.repositories.audit_log_repository import AuditLogRepository


class AuditLogService:
    """Query and append structured audit entries."""

    def __init__(self, *, audit_log_repository: AuditLogRepository) -> None:
        self._repo = audit_log_repository

    async def list_entries(
        self,
        *,
        company_id: str,
        user_id: str | None,
        date_from: datetime | None,
        date_to: datetime | None,
        transaction_types: list[str] | None = None,
        transaction_type_contains: str | None = None,
        transaction_id: str | None = None,
        take: int = 100,
    ):
        """Filter log grid like Settings → User Log."""

        return await self._repo.list_filtered(
            company_id=company_id,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
            transaction_types=transaction_types,
            transaction_type_contains=transaction_type_contains,
            transaction_id=transaction_id,
            take=take,
        )

    async def record(
        self,
        *,
        company_id: str,
        user_id: str | None,
        transaction_type: str,
        transaction_id: str | None,
        status: str | None,
        details: str | None,
    ):
        """Append one row after successful business operations."""

        return await self._repo.append(
            company_id=company_id,
            user_id=user_id,
            transaction_type=transaction_type,
            transaction_id=transaction_id,
            status=status,
            details=details,
        )
