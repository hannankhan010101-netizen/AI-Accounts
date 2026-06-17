"""Validate COA defaults and nominal codes before GL posting."""

from __future__ import annotations

from typing import Any

from app.core.exceptions import ValidationAppError
from app.repositories.coa_repository import CoaRepository
from app.repositories.smart_settings_repository import SmartSettingsRepository


class PostingPrerequisitesService:
    """Fail fast when posting configuration is incomplete."""

    def __init__(
        self,
        *,
        smart_settings_repository: SmartSettingsRepository,
        coa_repository: CoaRepository,
    ) -> None:
        self._smart_settings = smart_settings_repository
        self._coa = coa_repository

    async def defaults(self, *, company_id: str) -> dict[str, Any]:
        row = await self._smart_settings.get_for_company(company_id=company_id)
        if row is None or not isinstance(row.payload, dict):
            return {}
        block = row.payload.get("defaults")
        return block if isinstance(block, dict) else {}

    async def require_defaults(
        self,
        *,
        company_id: str,
        required_keys: list[str],
        context_label: str,
    ) -> dict[str, Any]:
        """Ensure Smart Settings ``defaults`` contains all ``required_keys``."""

        d = await self.defaults(company_id=company_id)
        missing = [k for k in required_keys if not d.get(k)]
        if missing:
            raise ValidationAppError(
                f"{context_label}: set Smart Settings → Defaults fields: {', '.join(missing)}"
            )
        return d

    async def require_nominal_codes_exist(
        self,
        *,
        company_id: str,
        codes: list[str],
        context_label: str,
    ) -> None:
        """Ensure each code exists on the company chart of accounts."""

        unique = sorted({c for c in codes if c})
        if not unique:
            return
        missing = await self._coa.missing_nominal_codes(
            company_id=company_id, codes=unique
        )
        if missing:
            raise ValidationAppError(
                f"{context_label}: unknown nominal code(s) on chart: {', '.join(missing)}"
            )

    async def require_sales_invoice_posting(self, *, company_id: str) -> dict[str, Any]:
        d = await self.require_defaults(
            company_id=company_id,
            required_keys=["receivablesNominalCode", "salesNominalCode"],
            context_label="Sales invoice posting",
        )
        codes = [d["receivablesNominalCode"], d["salesNominalCode"]]
        gst = d.get("gstOutputNominalCode")
        if gst:
            codes.append(gst)
        await self.require_nominal_codes_exist(
            company_id=company_id,
            codes=codes,
            context_label="Sales invoice posting",
        )
        return d

    async def require_supplier_bill_posting(self, *, company_id: str) -> dict[str, Any]:
        d = await self.require_defaults(
            company_id=company_id,
            required_keys=["purchasesNominalCode", "payablesNominalCode"],
            context_label="Supplier bill posting",
        )
        codes = [d["purchasesNominalCode"], d["payablesNominalCode"]]
        gst = d.get("gstInputNominalCode")
        if gst:
            codes.append(gst)
        await self.require_nominal_codes_exist(
            company_id=company_id,
            codes=codes,
            context_label="Supplier bill posting",
        )
        return d

    async def require_cogs_posting(self, *, company_id: str) -> dict[str, Any]:
        d = await self.require_defaults(
            company_id=company_id,
            required_keys=["cogsNominalCode", "inventoryNominalCode"],
            context_label="COGS posting",
        )
        await self.require_nominal_codes_exist(
            company_id=company_id,
            codes=[d["cogsNominalCode"], d["inventoryNominalCode"]],
            context_label="COGS posting",
        )
        return d

    async def require_stock_adjustment_posting(self, *, company_id: str) -> dict[str, Any]:
        d = await self.require_defaults(
            company_id=company_id,
            required_keys=["inventoryNominalCode", "stockAdjustmentNominalCode"],
            context_label="Stock adjustment posting",
        )
        await self.require_nominal_codes_exist(
            company_id=company_id,
            codes=[d["inventoryNominalCode"], d["stockAdjustmentNominalCode"]],
            context_label="Stock adjustment posting",
        )
        return d

    async def require_fx_posting(self, *, company_id: str) -> dict[str, Any]:
        d = await self.require_defaults(
            company_id=company_id,
            required_keys=["fxGainNominalCode", "fxLossNominalCode"],
            context_label="FX revaluation posting",
        )
        await self.require_nominal_codes_exist(
            company_id=company_id,
            codes=[d["fxGainNominalCode"], d["fxLossNominalCode"]],
            context_label="FX revaluation posting",
        )
        return d
