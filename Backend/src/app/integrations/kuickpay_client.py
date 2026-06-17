"""Kuickpay REST client — P7."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import httpx

from app.core.config import get_settings


class KuickpayClient:
    def __init__(self) -> None:
        self._settings = get_settings()

    @property
    def enabled(self) -> bool:
        s = self._settings
        return bool(
            s.kuickpay_enabled
            and s.kuickpay_api_url.strip()
            and s.kuickpay_merchant_id.strip()
        )

    async def create_checkout(
        self,
        *,
        merchant_ref: str,
        amount: Decimal,
        customer_id: str,
    ) -> dict[str, Any]:
        url = self._settings.kuickpay_api_url.rstrip("/")
        payload = {
            "merchantId": self._settings.kuickpay_merchant_id,
            "merchantRef": merchant_ref,
            "amount": str(amount),
            "customerId": customer_id,
        }
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._settings.kuickpay_api_key.strip():
            headers["Authorization"] = f"Bearer {self._settings.kuickpay_api_key}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{url}/checkout", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                return {"raw": data}
            return data
