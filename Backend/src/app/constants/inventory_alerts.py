"""Inventory alert constants — batch expiry (§7.8)."""

from __future__ import annotations

EXPIRY_ALERT_WINDOW_DAYS = 30

EXPIRY_STATUS_EXPIRED = "expired"
EXPIRY_STATUS_EXPIRING_SOON = "expiring_soon"
EXPIRY_STATUS_OK = "ok"
EXPIRY_STATUS_NO_EXPIRY = "no_expiry"
