"""P43 foundation unit tests."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest


@pytest.mark.asyncio
async def test_openapi_p43_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    base = "/api/v1/companies/{company_id}"
    assert f"{base}/bank-transfers/{{transfer_id}}" in paths
    assert "get" in paths[f"{base}/bank-transfers/{{transfer_id}}"]
    audit_get = paths[f"{base}/audit-log"]["get"]
    param_names = {p["name"] for p in audit_get.get("parameters", [])}
    assert "typeContains" in param_names


@pytest.mark.asyncio
async def test_audit_log_type_contains_filter() -> None:
    from unittest.mock import MagicMock

    from app.repositories.audit_log_repository import AuditLogRepository

    captured: dict = {}

    async def fake_find_many(*, where, order, take):
        captured["where"] = where
        return []

    db = MagicMock()
    db.auditlogentry.find_many = fake_find_many
    repo = AuditLogRepository(db)
    rows = await repo.list_filtered(
        company_id="c1",
        user_id=None,
        date_from=None,
        date_to=None,
        transaction_type_contains="BANK",
    )
    assert rows == []
    assert captured["where"]["transactionType"] == {"contains": "BANK"}
