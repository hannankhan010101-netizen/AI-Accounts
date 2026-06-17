"""Shared approval-policy guard before GL posting."""

from __future__ import annotations

from decimal import Decimal

from app.services.approval_engine_service import ApprovalEngineService


async def guard_document_post(
    engine: ApprovalEngineService,
    *,
    company_id: str,
    entity_type: str,
    entity_id: str,
    amount: Decimal | str | float,
) -> None:
    await engine.assert_can_post(
        company_id=company_id,
        entity_type=entity_type,
        entity_id=entity_id,
        amount=Decimal(str(amount)),
    )
