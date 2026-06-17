"""Load and merge invite/welcome email templates from Smart Settings — P30."""

from __future__ import annotations

from typing import Any

from app.constants.invite_email_defaults import (
    DEFAULT_INVITE_EMAIL_TEMPLATE,
    DEFAULT_WELCOME_EMAIL_TEMPLATE,
    INVITE_EMAIL_TEMPLATE_KEY,
    WELCOME_EMAIL_TEMPLATE_KEY,
)
from app.repositories.smart_settings_repository import SmartSettingsRepository


def _merge_template(defaults: dict[str, str], overrides: Any) -> dict[str, str]:
    if not isinstance(overrides, dict):
        return dict(defaults)
    out = dict(defaults)
    for key in defaults:
        val = overrides.get(key)
        if isinstance(val, str) and val.strip():
            out[key] = val.strip()
    return out


def apply_placeholders(template: dict[str, str], **values: str) -> dict[str, str]:
    """Replace ``{key}`` placeholders in subject/body fields."""

    out: dict[str, str] = {}
    for key, text in template.items():
        rendered = text
        for ph, val in values.items():
            rendered = rendered.replace(f"{{{ph}}}", val)
        out[key] = rendered
    return out


class InviteEmailTemplateService:
    def __init__(self, *, smart_settings_repository: SmartSettingsRepository) -> None:
        self._settings = smart_settings_repository

    async def _payload(self, *, company_id: str) -> dict[str, Any]:
        row = await self._settings.get_for_company(company_id=company_id)
        raw = row.payload if row else {}
        return raw if isinstance(raw, dict) else {}

    async def get_invite_template(self, *, company_id: str) -> dict[str, str]:
        payload = await self._payload(company_id=company_id)
        return _merge_template(
            DEFAULT_INVITE_EMAIL_TEMPLATE,
            payload.get(INVITE_EMAIL_TEMPLATE_KEY),
        )

    async def get_welcome_template(self, *, company_id: str) -> dict[str, str]:
        payload = await self._payload(company_id=company_id)
        return _merge_template(
            DEFAULT_WELCOME_EMAIL_TEMPLATE,
            payload.get(WELCOME_EMAIL_TEMPLATE_KEY),
        )

    async def save_invite_template(
        self,
        *,
        company_id: str,
        template: dict[str, str],
    ) -> dict[str, str]:
        payload = await self._payload(company_id=company_id)
        merged = _merge_template(DEFAULT_INVITE_EMAIL_TEMPLATE, template)
        payload[INVITE_EMAIL_TEMPLATE_KEY] = merged
        await self._settings.upsert_payload(company_id=company_id, payload=payload)
        return merged

    async def save_welcome_template(
        self,
        *,
        company_id: str,
        template: dict[str, str],
    ) -> dict[str, str]:
        payload = await self._payload(company_id=company_id)
        merged = _merge_template(DEFAULT_WELCOME_EMAIL_TEMPLATE, template)
        payload[WELCOME_EMAIL_TEMPLATE_KEY] = merged
        await self._settings.upsert_payload(company_id=company_id, payload=payload)
        return merged
