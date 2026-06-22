"""Tests for batch expiry alert classification."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.constants.inventory_alerts import (
    EXPIRY_STATUS_EXPIRED,
    EXPIRY_STATUS_EXPIRING_SOON,
    EXPIRY_STATUS_NO_EXPIRY,
    EXPIRY_STATUS_OK,
)
from app.services.batch_expiry_alert_service import BatchExpiryAlertService


def _dt(days_offset: int) -> datetime:
    base = datetime(2026, 6, 23, 12, 0, 0, tzinfo=UTC)
    return base + timedelta(days=days_offset)


def test_expired_batch() -> None:
    svc = BatchExpiryAlertService(window_days=30)
    now = _dt(0)
    result = svc.classify_batch(
        expiry_date=_dt(-1),
        quantity_on_hand=Decimal("10"),
        now=now,
    )
    assert result["expiryStatus"] == EXPIRY_STATUS_EXPIRED
    assert result["daysToExpiry"] == -1
    assert result["alertable"] is True


def test_expiring_soon_today() -> None:
    svc = BatchExpiryAlertService(window_days=30)
    now = _dt(0)
    result = svc.classify_batch(
        expiry_date=_dt(0),
        quantity_on_hand=Decimal("5"),
        now=now,
    )
    assert result["expiryStatus"] == EXPIRY_STATUS_EXPIRING_SOON
    assert result["daysToExpiry"] == 0


def test_expiring_soon_within_window() -> None:
    svc = BatchExpiryAlertService(window_days=30)
    now = _dt(0)
    result = svc.classify_batch(
        expiry_date=_dt(30),
        quantity_on_hand=Decimal("1"),
        now=now,
    )
    assert result["expiryStatus"] == EXPIRY_STATUS_EXPIRING_SOON
    assert result["daysToExpiry"] == 30


def test_ok_beyond_window() -> None:
    svc = BatchExpiryAlertService(window_days=30)
    now = _dt(0)
    result = svc.classify_batch(
        expiry_date=_dt(31),
        quantity_on_hand=Decimal("1"),
        now=now,
    )
    assert result["expiryStatus"] == EXPIRY_STATUS_OK
    assert result["alertable"] is False


def test_null_expiry_excluded() -> None:
    svc = BatchExpiryAlertService()
    result = svc.classify_batch(expiry_date=None, quantity_on_hand=Decimal("10"))
    assert result["expiryStatus"] == EXPIRY_STATUS_NO_EXPIRY
    assert result["alertable"] is False


def test_zero_qty_excluded() -> None:
    svc = BatchExpiryAlertService()
    result = svc.classify_batch(
        expiry_date=_dt(5),
        quantity_on_hand=Decimal("0"),
    )
    assert result["alertable"] is False


def test_summarize_rows() -> None:
    svc = BatchExpiryAlertService(window_days=30)
    now = _dt(0)
    rows = [
        {"productCode": "A", "batchNumber": "1", "expiryDate": _dt(-2), "quantityOnHand": "3"},
        {"productCode": "B", "batchNumber": "2", "expiryDate": _dt(10), "quantityOnHand": "1"},
        {"productCode": "C", "batchNumber": "3", "expiryDate": _dt(60), "quantityOnHand": "1"},
        {"productCode": "D", "batchNumber": "4", "expiryDate": None, "quantityOnHand": "5"},
    ]
    summary = svc.summarize_rows(rows, now=now)
    assert summary["expired"] == 1
    assert summary["expiringSoon"] == 1
    assert summary["totalAlertable"] == 2


def test_filter_expiring() -> None:
    svc = BatchExpiryAlertService(window_days=30)
    now = _dt(0)
    rows = [
        {"productCode": "A", "batchNumber": "1", "expiryDate": _dt(-1), "quantityOnHand": "1"},
        {"productCode": "B", "batchNumber": "2", "expiryDate": _dt(60), "quantityOnHand": "1"},
    ]
    filtered = svc.filter_rows(rows, filter_name="expiring", now=now)
    assert len(filtered) == 1
    assert filtered[0]["productCode"] == "A"
