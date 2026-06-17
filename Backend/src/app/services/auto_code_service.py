"""Smart Settings auto-code generation — catalog §12.2.8."""

from __future__ import annotations

from typing import Any

from app.core.exceptions import ValidationAppError
from app.repositories.document_number_repository import DocumentNumberRepository
from app.repositories.smart_settings_repository import SmartSettingsRepository

AUTO_CODE_ENTITIES = frozenset(
    {
        "customer",
        "supplier",
        "product",
        "location",
        "project",
        "wht",
        "gst",
        "adt",
        "fed",
        "nominal",
    }
)


class AutoCodeService:
    """Issue monotonic master codes from Smart Settings ``autoCodes`` blocks."""

    def __init__(
        self,
        *,
        smart_settings_repository: SmartSettingsRepository,
        document_number_repository: DocumentNumberRepository,
    ) -> None:
        self._smart = smart_settings_repository
        self._numbers = document_number_repository

    async def _config(self, *, company_id: str, entity_key: str) -> dict[str, Any] | None:
        if entity_key not in AUTO_CODE_ENTITIES:
            return None
        row = await self._smart.get_for_company(company_id=company_id)
        if row is None:
            return None
        payload = row.payload if isinstance(row.payload, dict) else {}
        auto_codes = payload.get("autoCodes") or {}
        if not isinstance(auto_codes, dict):
            return None
        cfg = auto_codes.get(entity_key)
        return cfg if isinstance(cfg, dict) else None

    def _format(self, *, prefix: str, serial: int) -> str:
        return f"{prefix}{serial}"

    async def is_enabled(self, *, company_id: str, entity_key: str) -> bool:
        cfg = await self._config(company_id=company_id, entity_key=entity_key)
        return bool(cfg and cfg.get("enabled"))

    async def peek_next(self, *, company_id: str, entity_key: str) -> str | None:
        """Preview the next code without consuming the sequence."""

        cfg = await self._config(company_id=company_id, entity_key=entity_key)
        if not cfg or not cfg.get("enabled"):
            return None
        prefix = str(cfg.get("prefix") or "")
        seq_key = f"auto:{entity_key}"
        existing = await self._numbers.peek_next(company_id=company_id, sequence_key=seq_key)
        if existing is not None:
            return self._format(prefix=prefix, serial=existing)
        start_raw = cfg.get("startSerial")
        if start_raw is not None and str(start_raw).strip():
            try:
                return self._format(prefix=prefix, serial=int(str(start_raw).strip()))
            except ValueError:
                pass
        return self._format(prefix=prefix, serial=1)

    async def reserve_next(self, *, company_id: str, entity_key: str) -> str:
        """Consume the next auto code for ``entity_key``."""

        cfg = await self._config(company_id=company_id, entity_key=entity_key)
        if not cfg or not cfg.get("enabled"):
            raise ValidationAppError(f"Auto code is not enabled for {entity_key}")
        prefix = str(cfg.get("prefix") or "")
        seq_key = f"auto:{entity_key}"
        existing = await self._numbers.peek_next(company_id=company_id, sequence_key=seq_key)
        if existing is None:
            start_raw = cfg.get("startSerial")
            if start_raw is not None and str(start_raw).strip():
                try:
                    start = int(str(start_raw).strip())
                    await self._numbers.seed_sequence(
                        company_id=company_id,
                        sequence_key=seq_key,
                        next_value=start + 1,
                    )
                    return self._format(prefix=prefix, serial=start)
                except ValueError:
                    pass
        serial = await self._numbers.reserve_next(
            company_id=company_id, sequence_key=seq_key
        )
        return self._format(prefix=prefix, serial=serial)

    async def resolve_code(
        self,
        *,
        company_id: str,
        entity_key: str,
        provided: str | None,
        required: bool = True,
    ) -> str:
        """Use ``provided`` when set; otherwise reserve from auto-code settings."""

        cleaned = (provided or "").strip()
        if cleaned:
            return cleaned
        if await self.is_enabled(company_id=company_id, entity_key=entity_key):
            return await self.reserve_next(company_id=company_id, entity_key=entity_key)
        if required:
            raise ValidationAppError("Code is required (enable auto code in Smart Settings)")
        raise ValidationAppError("Code is required")
