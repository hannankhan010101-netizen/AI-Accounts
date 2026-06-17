"""Security-sensitive audit events — P9."""

from __future__ import annotations

from app.repositories.audit_log_repository import AuditLogRepository


class SecurityAuditService:
    def __init__(self, *, audit_log_repository: AuditLogRepository) -> None:
        self._repo = audit_log_repository

    async def record(
        self,
        *,
        company_id: str,
        event_type: str,
        resource_id: str | None = None,
        status: str = "ok",
        details: str | None = None,
        user_id: str | None = None,
    ) -> None:
        await self._repo.append(
            company_id=company_id,
            user_id=user_id,
            transaction_type=f"security.{event_type}",
            transaction_id=resource_id,
            status=status,
            details=details,
        )
