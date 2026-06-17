"""PayPro REST client — P6 (optional live checkout)."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class PayproClient:
    def __init__(self) -> None:
        self._settings = get_settings()

    @property
    def enabled(self) -> bool:
        s = self._settings
        return bool(
            s.paypro_enabled
            and s.paypro_api_url.strip()
            and s.paypro_merchant_id.strip()
        )

    async def create_checkout(
        self,
        *,
        merchant_ref: str,
        amount: Decimal,
        customer_id: str,
    ) -> dict[str, Any]:
        url = self._settings.paypro_api_url.rstrip("/")
        payload = {
            "merchantId": self._settings.paypro_merchant_id,
            "merchantRef": merchant_ref,
            "amount": str(amount),
            "customerId": customer_id,
        }
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._settings.paypro_api_key.strip():
            headers["Authorization"] = f"Bearer {self._settings.paypro_api_key}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{url}/checkout", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                return {"raw": data}
            return data
