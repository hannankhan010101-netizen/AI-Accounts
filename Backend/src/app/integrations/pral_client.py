"""FBR PRAL HTTP client — P5 (optional live submission)."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class PralClient:
    def __init__(self) -> None:
        self._settings = get_settings()

    @property
    def enabled(self) -> bool:
        s = self._settings
        return bool(
            s.fbr_pral_enabled
            and s.fbr_pral_api_url.strip()
            and s.fbr_pral_api_key.strip()
        )

    async def submit_invoice(self, *, payload: dict[str, Any]) -> dict[str, Any]:
        """POST invoice payload to PRAL; raises on HTTP errors."""

        url = self._settings.fbr_pral_api_url.rstrip("/")
        headers = {
            "Authorization": f"Bearer {self._settings.fbr_pral_api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{url}/invoices", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                return {"raw": data}
            return data

    async def poll_invoice_status(self, *, fbr_reference: str) -> dict[str, Any]:
        """GET submission status from PRAL."""

        url = self._settings.fbr_pral_api_url.rstrip("/")
        headers = {
            "Authorization": f"Bearer {self._settings.fbr_pral_api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{url}/invoices/{fbr_reference}/status",
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                return {"raw": data, "status": "unknown"}
            return data
