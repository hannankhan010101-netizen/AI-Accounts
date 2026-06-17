"""Line tax calculation from Taxes & Year End config — catalog §3.12 / Sprint 10."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from app.repositories.taxes_config_repository import TaxesConfigRepository
from app.services.smart_settings_runtime import SmartSettingsRuntime


@dataclass(frozen=True, slots=True)
class TaxLeg:
    """One tax bucket to post (e.g. GST output)."""

    tax_code: str
    tax_rate: Decimal
    tax_base: Decimal
    tax_amount: Decimal
    nominal_code: str | None


@dataclass(frozen=True, slots=True)
class TaxedLine:
    """Repo-ready line dict after tax computation."""

    product_code: str | None
    quantity: Decimal
    rate: Decimal
    line_subtotal: Decimal
    gst_code: str | None
    gst_rate: Decimal
    tax_amount: Decimal
    line_total: Decimal
    project_code: str | None = None

    def to_repo_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "productCode": self.product_code,
            "quantity": self.quantity,
            "rate": self.rate,
            "lineSubtotal": self.line_subtotal,
            "gstCode": self.gst_code,
            "gstRate": self.gst_rate,
            "taxAmount": self.tax_amount,
            "lineTotal": self.line_total,
        }
        if self.project_code is not None:
            out["projectCode"] = self.project_code
        return out


@dataclass(frozen=True, slots=True)
class DocumentTaxResult:
    """Totals and journal tax legs for a sales/purchase document."""

    lines: list[TaxedLine]
    net_total: Decimal
    tax_total: Decimal
    gross_total: Decimal
    tax_legs: list[TaxLeg]
    summaries: list[dict[str, Any]]


def _quantize(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.0001"))


class TaxCalculationService:
    """Apply GST rates from tenant taxes config to document lines."""

    def __init__(
        self,
        *,
        taxes_repository: TaxesConfigRepository,
        smart_runtime: SmartSettingsRuntime | None = None,
    ) -> None:
        self._taxes = taxes_repository
        self._smart_runtime = smart_runtime

    async def _gst_rate_lookup(self, *, company_id: str) -> dict[str, dict[str, Any]]:
        return await self._rate_table(company_id=company_id, attr="gstRates")

    async def _rate_table(
        self, *, company_id: str, attr: str
    ) -> dict[str, dict[str, Any]]:
        row = await self._taxes.get_for_company(company_id=company_id)
        if row is None:
            return {}
        rates = getattr(row, attr, None)
        if not isinstance(rates, list):
            return {}
        lookup: dict[str, dict[str, Any]] = {}
        for item in rates:
            if not isinstance(item, dict):
                continue
            code = str(item.get("taxCode") or item.get("tax_code") or "").strip()
            if not code or str(item.get("status", "active")).lower() == "inactive":
                continue
            lookup[code.upper()] = item
        return lookup

    def _accumulate_leg(
        self,
        leg_map: dict[str, TaxLeg],
        *,
        code: str,
        rate: Decimal,
        subtotal: Decimal,
        tax_amount: Decimal,
        nominal: str | None,
    ) -> None:
        if tax_amount <= 0:
            return
        key = code.upper()
        existing = leg_map.get(key)
        if existing:
            leg_map[key] = TaxLeg(
                tax_code=key,
                tax_rate=rate,
                tax_base=existing.tax_base + subtotal,
                tax_amount=existing.tax_amount + tax_amount,
                nominal_code=existing.nominal_code or nominal,
            )
        else:
            leg_map[key] = TaxLeg(
                tax_code=key,
                tax_rate=rate,
                tax_base=subtotal,
                tax_amount=tax_amount,
                nominal_code=nominal,
            )

    def _resolve_rate(
        self,
        *,
        lookup: dict[str, dict[str, Any]],
        gst_code: str | None,
        gst_rate_override: Decimal | None,
    ) -> tuple[str | None, Decimal, str | None]:
        if gst_rate_override is not None and gst_rate_override > 0:
            code = (gst_code or "GST").upper()
            nominal = None
            if code in lookup:
                nominal = lookup[code].get("accountId") or lookup[code].get("account_id")
            return code, gst_rate_override, str(nominal) if nominal else None

        if not gst_code:
            return None, Decimal(0), None

        key = gst_code.upper()
        row = lookup.get(key)
        if not row:
            return key, Decimal(0), None
        rate = Decimal(str(row.get("taxRate") or row.get("tax_rate") or 0))
        nominal = row.get("accountId") or row.get("account_id")
        return key, rate, str(nominal) if nominal else None

    async def compute_sales_lines(
        self,
        *,
        company_id: str,
        raw_lines: list[dict[str, Any]],
    ) -> DocumentTaxResult:
        round_off = False
        if self._smart_runtime is not None:
            round_off = await self._smart_runtime.round_off_sales_enabled(
                company_id=company_id
            )
        lookup = await self._gst_rate_lookup(company_id=company_id)
        adt_lookup = await self._rate_table(company_id=company_id, attr="adtRates")
        fed_lookup = await self._rate_table(company_id=company_id, attr="fedRates")
        taxed: list[TaxedLine] = []
        leg_map: dict[str, TaxLeg] = {}

        for raw in raw_lines:
            qty = Decimal(str(raw["quantity"]))
            rate = Decimal(str(raw["rate"]))
            subtotal = _quantize(qty * rate)
            code, gst_rate, nominal = self._resolve_rate(
                lookup=lookup,
                gst_code=raw.get("gstCode") or raw.get("gst_code"),
                gst_rate_override=(
                    Decimal(str(raw["gstRate"]))
                    if raw.get("gstRate") is not None
                    else (
                        Decimal(str(raw["gst_rate"]))
                        if raw.get("gst_rate") is not None
                        else None
                    )
                ),
            )
            tax_amount = (
                _quantize(subtotal * gst_rate / Decimal(100)) if gst_rate > 0 else Decimal(0)
            )
            if tax_amount > 0 and code:
                self._accumulate_leg(
                    leg_map,
                    code=code,
                    rate=gst_rate,
                    subtotal=subtotal,
                    tax_amount=tax_amount,
                    nominal=nominal,
                )
            for tax_code_raw, table in (
                (raw.get("adtCode") or raw.get("adt_code"), adt_lookup),
                (raw.get("fedCode") or raw.get("fed_code"), fed_lookup),
            ):
                if not tax_code_raw:
                    continue
                tkey = str(tax_code_raw).upper()
                trow = table.get(tkey, {})
                trate = Decimal(str(trow.get("taxRate") or trow.get("tax_rate") or 0))
                if trate <= 0:
                    continue
                tamount = _quantize(subtotal * trate / Decimal(100))
                tnominal = trow.get("accountId") or trow.get("account_id")
                tax_amount += tamount
                self._accumulate_leg(
                    leg_map,
                    code=tkey,
                    rate=trate,
                    subtotal=subtotal,
                    tax_amount=tamount,
                    nominal=str(tnominal) if tnominal else None,
                )
            line_total = subtotal + tax_amount
            if round_off and self._smart_runtime is not None:
                line_total = self._smart_runtime.apply_round_off(line_total)
            taxed.append(
                TaxedLine(
                    product_code=raw.get("productCode") or raw.get("product_code"),
                    quantity=qty,
                    rate=rate,
                    line_subtotal=subtotal,
                    gst_code=code,
                    gst_rate=gst_rate,
                    tax_amount=tax_amount,
                    line_total=line_total,
                    project_code=raw.get("projectCode") or raw.get("project_code"),
                )
            )

        net = sum((l.line_subtotal for l in taxed), Decimal(0))
        tax = sum((l.tax_amount for l in taxed), Decimal(0))
        legs = list(leg_map.values())
        summaries = [
            {
                "taxCode": leg.tax_code.lower(),
                "taxRate": leg.tax_rate,
                "taxBase": leg.tax_base,
                "taxAmount": leg.tax_amount,
                "nominalCode": leg.nominal_code,
            }
            for leg in legs
        ]
        return DocumentTaxResult(
            lines=taxed,
            net_total=net,
            tax_total=tax,
            gross_total=net + tax,
            tax_legs=legs,
            summaries=summaries,
        )

    compute_purchase_lines = compute_sales_lines

    async def wht_nominal_for_code(
        self, *, company_id: str, wht_code: str
    ) -> str | None:
        """Resolve WHT control nominal from taxes config."""

        lookup = await self._rate_table(company_id=company_id, attr="whtRates")
        row = lookup.get(wht_code.upper())
        if not row:
            return None
        nominal = row.get("accountId") or row.get("account_id")
        return str(nominal) if nominal else None

    async def persist_tax_summaries(
        self,
        *,
        company_id: str,
        document_kind: str,
        document_id: str,
        summaries: list[dict[str, Any]],
        db: Any,
    ) -> None:
        """Write ``DocumentTaxSummary`` rows (requires Prisma client)."""

        for s in summaries:
            await db.documenttaxsummary.create(
                data={
                    "companyId": company_id,
                    "documentKind": document_kind,
                    "documentId": document_id,
                    "taxCode": str(s["taxCode"]),
                    "taxRate": s["taxRate"],
                    "taxBase": s["taxBase"],
                    "taxAmount": s["taxAmount"],
                    "nominalCode": s.get("nominalCode"),
                }
            )
