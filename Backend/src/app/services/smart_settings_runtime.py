"""Read Smart Settings payload and apply FA §12.2 runtime rules."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from prisma_generated import Prisma

from app.core.exceptions import ValidationAppError
from app.repositories.smart_settings_repository import SmartSettingsRepository
from app.services.aging_service import AgingService


class SmartSettingsRuntime:
    def __init__(
        self,
        *,
        smart_settings_repository: SmartSettingsRepository,
        prisma: Prisma,
    ) -> None:
        self._smart = smart_settings_repository
        self._db = prisma
        self._aging = AgingService(prisma)

    async def payload(self, *, company_id: str) -> dict[str, Any]:
        row = await self._smart.get_for_company(company_id=company_id)
        if row is None or not isinstance(row.payload, dict):
            return {}
        return row.payload

    async def others_flag(self, *, company_id: str, key: str) -> bool:
        data = await self.payload(company_id=company_id)
        others = data.get("others")
        if not isinstance(others, dict):
            return False
        return bool(others.get(key))

    async def round_off_sales_enabled(self, *, company_id: str) -> bool:
        return await self.others_flag(company_id=company_id, key="roundOffSales")

    def apply_round_off(self, amount: Decimal) -> Decimal:
        """Round to whole currency units (FA round-off sales)."""

        return amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP)

    async def assert_credit_limit(
        self,
        *,
        company_id: str,
        customer_id: str,
        additional_amount: Decimal,
        for_sales_order: bool = False,
    ) -> None:
        """Block when open AR + new amount exceeds customer credit limit."""

        flag_key = "applySoCreditLimit" if for_sales_order else "applyCreditLimit"
        if not await self.others_flag(company_id=company_id, key=flag_key):
            return
        customer = await self._db.customer.find_first(
            where={"id": customer_id, "companyId": company_id},
        )
        if customer is None:
            return
        fields = customer.customFields if isinstance(customer.customFields, dict) else {}
        raw_limit = fields.get("creditLimit") or fields.get("credit_limit")
        if raw_limit is None or str(raw_limit).strip() == "":
            return
        try:
            limit = Decimal(str(raw_limit))
        except Exception:  # noqa: BLE001
            return
        aging = await self._aging.ar_aging(company_id=company_id, as_of_date=None)
        open_balance = Decimal(0)
        for row in aging.get("rows") or []:
            if row.get("partyId") == customer_id:
                open_balance = Decimal(str(row.get("balance") or 0))
                break
        projected = open_balance + additional_amount
        if projected > limit:
            raise ValidationAppError(
                f"Credit limit exceeded: limit {limit}, projected balance {projected}."
            )

    async def template_draft_enabled(self, *, company_id: str, module_key: str) -> bool:
        data = await self.payload(company_id=company_id)
        block = data.get("templateDraft")
        if not isinstance(block, dict):
            return False
        return bool(block.get(module_key))

    async def post_gl_on_create(self, *, company_id: str, module_key: str) -> bool:
        """When template/draft is on for a module, save without GL until explicit post."""

        if await self.template_draft_enabled(company_id=company_id, module_key=module_key):
            return False
        return True

    async def product_description_labels(
        self, *, company_id: str, doc_type: str
    ) -> list[str]:
        """Column labels from Smart Settings product description matrix for a doc type."""

        data = await self.payload(company_id=company_id)
        rows = data.get("productDescription")
        if not isinstance(rows, list):
            return []
        labels: list[str] = []
        needle = doc_type.upper()
        for row in rows:
            if not isinstance(row, dict):
                continue
            types_raw = str(row.get("transactionTypes") or row.get("types") or "").upper()
            if types_raw and needle not in types_raw and "ALL" not in types_raw:
                continue
            label = str(row.get("label") or row.get("displayName") or "").strip()
            if label:
                labels.append(label)
        return labels

    def apply_product_description_defaults(
        self,
        *,
        repo_lines: list[dict[str, Any]],
        request_lines: list[Any],
        labels: list[str],
    ) -> list[dict[str, Any]]:
        """Fill empty ``descriptionFields`` keys from configured column labels."""

        if not labels:
            return repo_lines
        out: list[dict[str, Any]] = []
        for i, row in enumerate(repo_lines):
            merged = dict(row)
            fields: dict[str, str] = {}
            if i < len(request_lines):
                raw = getattr(request_lines[i], "description_fields", None)
                if isinstance(raw, dict):
                    fields = {str(k): str(v) for k, v in raw.items() if v is not None}
            for j, label in enumerate(labels[:8], start=1):
                key = f"col{j}"
                if key not in fields and label:
                    fields[key] = label
            if fields:
                merged["descriptionFields"] = fields
            out.append(merged)
        return out
