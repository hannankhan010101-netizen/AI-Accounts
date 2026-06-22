"""Batch expiry classification and summaries for in-app alerts."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any

from app.constants.inventory_alerts import (
    EXPIRY_ALERT_WINDOW_DAYS,
    EXPIRY_STATUS_EXPIRED,
    EXPIRY_STATUS_EXPIRING_SOON,
    EXPIRY_STATUS_NO_EXPIRY,
    EXPIRY_STATUS_OK,
)


def _to_utc_date(value: datetime | date | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if value.tzinfo is None:
        return value.date()
    return value.astimezone(UTC).date()


def _qty_positive(quantity: Any) -> bool:
    if quantity is None:
        return False
    try:
        return Decimal(str(quantity)) > 0
    except Exception:
        return False


class BatchExpiryAlertService:
    """Classify product batches by expiry urgency (UTC calendar dates)."""

    def __init__(self, *, window_days: int = EXPIRY_ALERT_WINDOW_DAYS) -> None:
        self._window_days = window_days

    def classify_batch(
        self,
        *,
        expiry_date: datetime | date | None,
        quantity_on_hand: Any,
        now: datetime | None = None,
    ) -> dict[str, Any]:
        """Return status, daysToExpiry, and whether the batch counts toward alerts."""

        if not _qty_positive(quantity_on_hand):
            return {
                "expiryStatus": EXPIRY_STATUS_NO_EXPIRY,
                "daysToExpiry": None,
                "alertable": False,
            }

        exp = _to_utc_date(expiry_date)
        if exp is None:
            return {
                "expiryStatus": EXPIRY_STATUS_NO_EXPIRY,
                "daysToExpiry": None,
                "alertable": False,
            }

        today = _to_utc_date(now or datetime.now(UTC))
        assert today is not None
        days_left = (exp - today).days

        if days_left < 0:
            status = EXPIRY_STATUS_EXPIRED
        elif days_left <= self._window_days:
            status = EXPIRY_STATUS_EXPIRING_SOON
        else:
            status = EXPIRY_STATUS_OK

        return {
            "expiryStatus": status,
            "daysToExpiry": days_left,
            "alertable": status in (EXPIRY_STATUS_EXPIRED, EXPIRY_STATUS_EXPIRING_SOON),
        }

    def enrich_row(self, row: Any, *, now: datetime | None = None) -> dict[str, Any]:
        """Merge expiry fields onto a batch dict or model."""

        if isinstance(row, dict):
            data = dict(row)
            expiry = data.get("expiryDate") or data.get("expiry_date")
            qty = data.get("quantityOnHand") or data.get("quantity_on_hand")
        else:
            data = {
                "id": row.id,
                "productCode": row.productCode,
                "batchNumber": row.batchNumber,
                "expiryDate": row.expiryDate,
                "quantityOnHand": row.quantityOnHand,
                "notes": row.notes,
                "createdAt": row.createdAt,
            }
            expiry = row.expiryDate
            qty = row.quantityOnHand

        meta = self.classify_batch(
            expiry_date=expiry,
            quantity_on_hand=qty,
            now=now,
        )
        data["expiryStatus"] = meta["expiryStatus"]
        data["daysToExpiry"] = meta["daysToExpiry"]
        return data

    def summarize_rows(
        self,
        rows: list[Any],
        *,
        now: datetime | None = None,
        preview_limit: int = 5,
    ) -> dict[str, Any]:
        """Aggregate counts and preview rows for command center."""

        expired = 0
        expiring_soon = 0
        preview: list[dict[str, Any]] = []

        for row in rows:
            enriched = self.enrich_row(row, now=now)
            status = enriched.get("expiryStatus")
            if status == EXPIRY_STATUS_EXPIRED:
                expired += 1
                if len(preview) < preview_limit:
                    preview.append(enriched)
            elif status == EXPIRY_STATUS_EXPIRING_SOON:
                expiring_soon += 1
                if len(preview) < preview_limit:
                    preview.append(enriched)

        preview.sort(
            key=lambda r: (
                0 if r.get("expiryStatus") == EXPIRY_STATUS_EXPIRED else 1,
                r.get("daysToExpiry") if r.get("daysToExpiry") is not None else 9999,
            )
        )

        return {
            "windowDays": self._window_days,
            "expired": expired,
            "expiringSoon": expiring_soon,
            "totalAlertable": expired + expiring_soon,
            "preview": preview[:preview_limit],
        }

    def filter_rows(
        self,
        rows: list[Any],
        *,
        filter_name: str | None,
        now: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Filter enriched rows by alert filter (expired | expiring | all)."""

        enriched = [self.enrich_row(r, now=now) for r in rows]
        if not filter_name or filter_name == "all":
            return enriched

        if filter_name == "expired":
            return [r for r in enriched if r.get("expiryStatus") == EXPIRY_STATUS_EXPIRED]
        if filter_name == "expiring":
            return [
                r
                for r in enriched
                if r.get("expiryStatus") in (EXPIRY_STATUS_EXPIRED, EXPIRY_STATUS_EXPIRING_SOON)
            ]
        return enriched
