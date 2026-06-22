"""Tests for expiry notification list builder."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.expiry_notification_service import list_expiry_notifications


@pytest.mark.asyncio
async def test_list_expiry_notifications_builds_items() -> None:
    now = datetime(2026, 6, 23, tzinfo=UTC)
    row = SimpleNamespace(
        id="batch1",
        productCode="SKU-1",
        batchNumber="B-1",
        expiryDate=now + timedelta(days=5),
        quantityOnHand=Decimal("10"),
        notes=None,
        createdAt=now,
    )
    batch_repo = MagicMock()
    batch_repo.list_expiring_batches = AsyncMock(return_value=[row])
    smart_runtime = MagicMock()
    smart_runtime.inventory_alerts_config = AsyncMock(
        return_value={"enabled": True, "windowDays": 30, "emailDigestEnabled": False}
    )

    items = await list_expiry_notifications(
        company_id="co1",
        batch_repo=batch_repo,
        smart_runtime=smart_runtime,
    )
    assert len(items) == 1
    assert items[0]["type"] == "batch_expiry"
    assert items[0]["severity"] == "warn"


@pytest.mark.asyncio
async def test_list_expiry_notifications_disabled() -> None:
    batch_repo = MagicMock()
    smart_runtime = MagicMock()
    smart_runtime.inventory_alerts_config = AsyncMock(
        return_value={"enabled": False, "windowDays": 30}
    )

    items = await list_expiry_notifications(
        company_id="co1",
        batch_repo=batch_repo,
        smart_runtime=smart_runtime,
    )
    assert items == []
    batch_repo.list_expiring_batches.assert_not_called()


@pytest.mark.asyncio
async def test_send_expiry_digest_skips_when_sent_recently() -> None:
    from app.services.expiry_notification_service import send_expiry_digest_if_due

    recent = (datetime.now(UTC) - timedelta(hours=2)).isoformat()
    smart_runtime = MagicMock()
    smart_runtime.inventory_alerts_config = AsyncMock(
        return_value={
            "enabled": True,
            "windowDays": 30,
            "emailDigestEnabled": True,
            "lastDigestSentAt": recent,
        }
    )
    email_service = MagicMock()
    email_service.is_configured.return_value = True

    ok, message = await send_expiry_digest_if_due(
        company_id="co1",
        company_name="Co",
        to_email="u@example.com",
        user_name="User",
        batch_repo=MagicMock(),
        smart_runtime=smart_runtime,
        smart_repo=MagicMock(),
        email_service=email_service,
        app_base_url="http://localhost:3000",
    )
    assert ok is False
    assert "24 hours" in message
    email_service.send_transactional_email.assert_not_called()
