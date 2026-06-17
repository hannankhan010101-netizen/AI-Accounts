"""Company-scoped application settings stored in SmartSettings.payload slices."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any

from app.constants.command_center_catalog import (
    DEFAULT_COMMAND_CENTER_WIDGETS,
    DEFAULT_DASHBOARD_VIEW,
)
from app.constants.dashboard_catalog import DEFAULT_DASHBOARD_WIDGETS
from app.constants.forms_catalog import FORM_BY_ID, FORM_CATALOG, default_form_layout
from app.constants.op_methods_catalog import DEFAULT_OP_METHODS_SETTINGS
from app.constants.listing_catalog import (
    LISTING_BY_ID,
    LISTING_CATALOG,
    default_listing_layout,
)
from app.constants.menu_catalog import MENU_BY_HREF, MENU_CATALOG, default_menu_layout
from app.constants.print_template_catalog import (
    PRINT_TEMPLATE_BY_CODE,
    PRINT_TEMPLATE_CATALOG,
    default_print_template,
)
from app.core.exceptions import NotFoundError, ValidationAppError
from app.repositories.smart_settings_repository import SmartSettingsRepository


def _deep_merge(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(base)
    for key, val in patch.items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], val)
        else:
            out[key] = val
    return out


class AppSettingsService:
    """Typed accessors for printing, content, filters, email, and misc settings."""

    def __init__(self, *, smart_settings_repository: SmartSettingsRepository) -> None:
        self._repo = smart_settings_repository

    async def _payload(self, *, company_id: str) -> dict[str, Any]:
        row = await self._repo.get_for_company(company_id=company_id)
        raw = row.payload if row else {}
        return raw if isinstance(raw, dict) else {}

    async def _save_slice(
        self, *, company_id: str, key: str, value: dict[str, Any]
    ) -> dict[str, Any]:
        current = await self._payload(company_id=company_id)
        merged = _deep_merge(current, {key: value})
        row = await self._repo.upsert_payload(company_id=company_id, payload=merged)
        saved = row.payload if isinstance(row.payload, dict) else {}
        slice_val = saved.get(key)
        return slice_val if isinstance(slice_val, dict) else value

    # --- Print templates ---

    def list_print_templates(self) -> list[dict[str, object]]:
        return [
            {
                "code": t.code,
                "label": t.label,
                "group": t.group,
                "supportsTwoCopies": t.supports_two_copies,
                "printModes": list(t.print_modes),
            }
            for t in PRINT_TEMPLATE_CATALOG
        ]

    async def get_print_template(self, *, company_id: str, code: str) -> dict[str, object]:
        if code not in PRINT_TEMPLATE_BY_CODE:
            raise NotFoundError(f"Unknown print template: {code}")
        payload = await self._payload(company_id=company_id)
        printing = payload.get("printing") if isinstance(payload.get("printing"), dict) else {}
        stored = printing.get(code) if isinstance(printing.get(code), dict) else {}
        defaults = default_print_template(code)
        return {**defaults, **stored, "code": code}

    async def put_print_template(
        self, *, company_id: str, code: str, body: dict[str, Any]
    ) -> dict[str, object]:
        if code not in PRINT_TEMPLATE_BY_CODE:
            raise NotFoundError(f"Unknown print template: {code}")
        payload = await self._payload(company_id=company_id)
        printing = payload.get("printing") if isinstance(payload.get("printing"), dict) else {}
        current = printing.get(code) if isinstance(printing.get(code), dict) else {}
        merged = {**default_print_template(code), **current, **body, "code": code}
        await self._save_slice(company_id=company_id, key="printing", value={**printing, code: merged})
        return merged

    # --- Content / listing layouts ---

    def list_listings(self) -> list[dict[str, object]]:
        return [
            {"id": l.id, "label": l.label, "branch": l.branch}
            for l in LISTING_CATALOG
        ]

    async def get_listing_layout(self, *, company_id: str, listing_id: str) -> dict[str, object]:
        if listing_id not in LISTING_BY_ID:
            raise NotFoundError(f"Unknown listing: {listing_id}")
        payload = await self._payload(company_id=company_id)
        content = payload.get("contentSettings") if isinstance(payload.get("contentSettings"), dict) else {}
        listings = content.get("listings") if isinstance(content.get("listings"), dict) else {}
        stored = listings.get(listing_id) if isinstance(listings.get(listing_id), dict) else {}
        defaults = default_listing_layout(listing_id)
        cols = stored.get("columns") if isinstance(stored.get("columns"), list) else defaults["columns"]
        return {"listingId": listing_id, "columns": cols}

    async def put_listing_layout(
        self, *, company_id: str, listing_id: str, body: dict[str, Any]
    ) -> dict[str, object]:
        if listing_id not in LISTING_BY_ID:
            raise NotFoundError(f"Unknown listing: {listing_id}")
        columns = body.get("columns")
        if not isinstance(columns, list):
            raise ValidationAppError("columns array required")
        payload = await self._payload(company_id=company_id)
        content = payload.get("contentSettings") if isinstance(payload.get("contentSettings"), dict) else {}
        listings = content.get("listings") if isinstance(content.get("listings"), dict) else {}
        layout = {"listingId": listing_id, "columns": columns}
        await self._save_slice(
            company_id=company_id,
            key="contentSettings",
            value={**content, "listings": {**listings, listing_id: layout}},
        )
        return layout

    def list_forms(self) -> list[dict[str, object]]:
        return [{"id": f.id, "label": f.label, "branch": f.branch} for f in FORM_CATALOG]

    async def get_form_layout(self, *, company_id: str, form_id: str) -> dict[str, object]:
        if form_id not in FORM_BY_ID:
            raise NotFoundError(f"Unknown form: {form_id}")
        payload = await self._payload(company_id=company_id)
        content = payload.get("contentSettings") if isinstance(payload.get("contentSettings"), dict) else {}
        forms = content.get("forms") if isinstance(content.get("forms"), dict) else {}
        stored = forms.get(form_id) if isinstance(forms.get(form_id), dict) else {}
        defaults = default_form_layout(form_id)
        fields = stored.get("fields") if isinstance(stored.get("fields"), list) else defaults["fields"]
        return {"formId": form_id, "fields": fields}

    async def put_form_layout(
        self, *, company_id: str, form_id: str, body: dict[str, Any]
    ) -> dict[str, object]:
        if form_id not in FORM_BY_ID:
            raise NotFoundError(f"Unknown form: {form_id}")
        fields = body.get("fields")
        if not isinstance(fields, list):
            raise ValidationAppError("fields array required")
        payload = await self._payload(company_id=company_id)
        content = payload.get("contentSettings") if isinstance(payload.get("contentSettings"), dict) else {}
        forms = content.get("forms") if isinstance(content.get("forms"), dict) else {}
        layout = {"formId": form_id, "fields": fields}
        await self._save_slice(
            company_id=company_id,
            key="contentSettings",
            value={**content, "forms": {**forms, form_id: layout}},
        )
        return layout

    async def get_menu_layout(self, *, company_id: str) -> dict[str, object]:
        payload = await self._payload(company_id=company_id)
        content = payload.get("contentSettings") if isinstance(payload.get("contentSettings"), dict) else {}
        stored = content.get("menu") if isinstance(content.get("menu"), dict) else {}
        defaults = default_menu_layout()
        items = stored.get("items") if isinstance(stored.get("items"), list) else defaults["items"]
        return {"items": items}

    @staticmethod
    def menu_etag(revision_token: str) -> str:
        return hashlib.sha256(revision_token.encode()).hexdigest()[:32]

    async def menu_revision_token(self, *, company_id: str) -> str:
        layout = await self.get_menu_layout(company_id=company_id)
        return json.dumps(layout.get("items"), sort_keys=True, default=str)

    async def put_menu_layout(self, *, company_id: str, body: dict[str, Any]) -> dict[str, object]:
        items = body.get("items")
        if not isinstance(items, list):
            raise ValidationAppError("items array required")
        for row in items:
            href = row.get("href") if isinstance(row, dict) else None
            if href not in MENU_BY_HREF:
                raise ValidationAppError(f"Unknown menu href: {href}")
        payload = await self._payload(company_id=company_id)
        content = payload.get("contentSettings") if isinstance(payload.get("contentSettings"), dict) else {}
        layout = {"items": items}
        await self._save_slice(
            company_id=company_id,
            key="contentSettings",
            value={**content, "menu": layout},
        )
        return layout

    # --- Generic slices ---

    async def get_slice(self, *, company_id: str, key: str, defaults: dict[str, Any]) -> dict[str, Any]:
        payload = await self._payload(company_id=company_id)
        stored = payload.get(key) if isinstance(payload.get(key), dict) else {}
        return {**defaults, **stored}

    async def put_slice(
        self, *, company_id: str, key: str, body: dict[str, Any], defaults: dict[str, Any]
    ) -> dict[str, Any]:
        payload = await self._payload(company_id=company_id)
        stored = payload.get(key) if isinstance(payload.get(key), dict) else {}
        merged = {**defaults, **stored, **body}
        await self._save_slice(company_id=company_id, key=key, value=merged)
        return merged

    async def get_filters_settings(self, *, company_id: str) -> dict[str, Any]:
        return await self.get_slice(
            company_id=company_id,
            key="filtersManagement",
            defaults={"persistUserFilters": True, "defaultDateRange": "thisMonth"},
        )

    async def put_filters_settings(self, *, company_id: str, body: dict[str, Any]) -> dict[str, Any]:
        return await self.put_slice(
            company_id=company_id,
            key="filtersManagement",
            body=body,
            defaults={"persistUserFilters": True, "defaultDateRange": "thisMonth"},
        )

    async def get_columns_settings(self, *, company_id: str) -> dict[str, Any]:
        return await self.get_slice(
            company_id=company_id,
            key="columnManagement",
            defaults={"allowUserOverrides": False, "syncWithContentSettings": True},
        )

    async def put_columns_settings(self, *, company_id: str, body: dict[str, Any]) -> dict[str, Any]:
        return await self.put_slice(
            company_id=company_id,
            key="columnManagement",
            body=body,
            defaults={"allowUserOverrides": False, "syncWithContentSettings": True},
        )

    async def get_email_settings(self, *, company_id: str) -> dict[str, Any]:
        return await self.get_slice(
            company_id=company_id,
            key="emailSettings",
            defaults={
                "smtpHost": "",
                "smtpPort": 587,
                "fromAddress": "",
                "useTls": True,
                "sendInvoiceEmail": False,
                "sendBalanceReminder": False,
            },
        )

    async def put_email_settings(self, *, company_id: str, body: dict[str, Any]) -> dict[str, Any]:
        return await self.put_slice(
            company_id=company_id,
            key="emailSettings",
            body=body,
            defaults={
                "smtpHost": "",
                "smtpPort": 587,
                "fromAddress": "",
                "useTls": True,
                "sendInvoiceEmail": False,
                "sendBalanceReminder": False,
            },
        )

    async def get_dashboard_settings(self, *, company_id: str) -> dict[str, Any]:
        defaults = {
            "widgets": list(DEFAULT_COMMAND_CENTER_WIDGETS),
            "views": [DEFAULT_DASHBOARD_VIEW],
            "activeViewId": "default",
        }
        stored = await self.get_slice(
            company_id=company_id,
            key="dashboardManagement",
            defaults=defaults,
        )
        if not isinstance(stored.get("views"), list) or not stored.get("views"):
            stored["views"] = [DEFAULT_DASHBOARD_VIEW]
        if not stored.get("activeViewId"):
            stored["activeViewId"] = "default"
        if not isinstance(stored.get("widgets"), list) or not stored.get("widgets"):
            stored["widgets"] = list(DEFAULT_COMMAND_CENTER_WIDGETS)
        return stored

    async def put_dashboard_settings(self, *, company_id: str, body: dict[str, Any]) -> dict[str, Any]:
        defaults = {
            "widgets": list(DEFAULT_COMMAND_CENTER_WIDGETS),
            "views": [DEFAULT_DASHBOARD_VIEW],
            "activeViewId": "default",
        }
        return await self.put_slice(
            company_id=company_id,
            key="dashboardManagement",
            body=body,
            defaults=defaults,
        )

    async def get_advance_users_settings(self, *, company_id: str) -> dict[str, Any]:
        return await self.get_slice(
            company_id=company_id,
            key="advanceUsers",
            defaults={"rules": []},
        )

    async def put_advance_users_settings(
        self, *, company_id: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        rules = body.get("rules")
        if rules is not None and not isinstance(rules, list):
            raise ValidationAppError("rules must be an array")
        return await self.put_slice(
            company_id=company_id,
            key="advanceUsers",
            body=body,
            defaults={"rules": []},
        )

    async def get_op_methods_settings(self, *, company_id: str) -> dict[str, Any]:
        return await self.get_slice(
            company_id=company_id,
            key="opMethods",
            defaults=dict(DEFAULT_OP_METHODS_SETTINGS),
        )

    async def put_op_methods_settings(self, *, company_id: str, body: dict[str, Any]) -> dict[str, Any]:
        return await self.put_slice(
            company_id=company_id,
            key="opMethods",
            body=body,
            defaults=dict(DEFAULT_OP_METHODS_SETTINGS),
        )

    async def get_missed_recurrence_settings(self, *, company_id: str) -> dict[str, Any]:
        return await self.get_slice(
            company_id=company_id,
            key="missedRecurrence",
            defaults={"notifyAdmin": True, "autoSkip": False, "lookbackDays": 30},
        )

    async def put_missed_recurrence_settings(
        self, *, company_id: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        return await self.put_slice(
            company_id=company_id,
            key="missedRecurrence",
            body=body,
            defaults={"notifyAdmin": True, "autoSkip": False, "lookbackDays": 30},
        )

    async def list_sent_emails(self, *, company_id: str) -> list[dict[str, Any]]:
        payload = await self._payload(company_id=company_id)
        log = payload.get("sentEmailLog")
        if isinstance(log, dict) and isinstance(log.get("entries"), list):
            return list(log["entries"])
        return []

    async def append_sent_email(
        self, *, company_id: str, entry: dict[str, Any], max_entries: int = 200
    ) -> None:
        from datetime import UTC, datetime

        payload = await self._payload(company_id=company_id)
        log = payload.get("sentEmailLog")
        if not isinstance(log, dict):
            log = {"entries": []}
        entries = log.get("entries")
        if not isinstance(entries, list):
            entries = []
        stamped = {
            **entry,
            "sentAt": entry.get("sentAt") or datetime.now(UTC).isoformat(),
        }
        entries = [stamped, *entries][:max_entries]
        await self._save_slice(
            company_id=company_id,
            key="sentEmailLog",
            value={"entries": entries},
        )
