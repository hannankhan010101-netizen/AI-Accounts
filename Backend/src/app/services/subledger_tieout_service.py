"""AR/AP sub-ledger vs GL control account tie-out — P1.3."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from prisma_generated import Prisma

from app.repositories.smart_settings_repository import SmartSettingsRepository
from app.services.aging_service import AgingService


class SubledgerTieoutService:
    def __init__(
        self,
        *,
        prisma: Prisma,
        smart_settings_repository: SmartSettingsRepository,
    ) -> None:
        self._db = prisma
        self._smart_settings = smart_settings_repository
        self._aging = AgingService(prisma)

    async def _defaults(self, *, company_id: str) -> dict:
        row = await self._smart_settings.get_for_company(company_id=company_id)
        if row is None or not isinstance(row.payload, dict):
            return {}
        block = row.payload.get("defaults")
        return block if isinstance(block, dict) else {}

    async def _gl_balance_for_nominal(
        self, *, company_id: str, nominal_code: str, as_of: datetime | None
    ) -> Decimal:
        journal_filter: dict = {"companyId": company_id, "status": "posted"}
        if as_of is not None:
            journal_filter["journalDate"] = {"lte": as_of}
        lines = await self._db.journalline.find_many(
            where={
                "nominalCode": nominal_code,
                "journal": {"is": journal_filter},
            },
            take=100_000,
        )
        return sum((line.debit - line.credit for line in lines), Decimal(0))

    async def ar_tieout(self, *, company_id: str, as_of_date: datetime | None = None) -> dict:
        as_of = as_of_date or datetime.now(timezone.utc)
        defaults = await self._defaults(company_id=company_id)
        ar_code = defaults.get("receivablesNominalCode")
        if not ar_code:
            return {
                "ok": False,
                "message": "receivablesNominalCode not set in Smart Settings → Defaults",
            }

        gl_balance = await self._gl_balance_for_nominal(
            company_id=company_id, nominal_code=ar_code, as_of=as_of
        )
        aging = await self._aging.ar_aging(company_id=company_id, as_of_date=as_of)
        subledger_total = Decimal(str(aging.get("totals", {}).get("outstanding", 0)))

        difference = gl_balance - subledger_total
        return {
            "ok": difference == 0,
            "controlNominalCode": ar_code,
            "glBalance": str(gl_balance),
            "subledgerBalance": str(subledger_total),
            "difference": str(difference),
            "asOf": as_of.isoformat(),
            "note": "Sub-ledger uses open invoice balances minus unallocated receipts (AgingService).",
        }

    async def ap_tieout(self, *, company_id: str, as_of_date: datetime | None = None) -> dict:
        as_of = as_of_date or datetime.now(timezone.utc)
        defaults = await self._defaults(company_id=company_id)
        ap_code = defaults.get("payablesNominalCode")
        if not ap_code:
            return {
                "ok": False,
                "message": "payablesNominalCode not set in Smart Settings → Defaults",
            }

        gl_balance = await self._gl_balance_for_nominal(
            company_id=company_id, nominal_code=ap_code, as_of=as_of
        )
        aging = await self._aging.ap_aging(company_id=company_id, as_of_date=as_of)
        subledger_total = Decimal(str(aging.get("totals", {}).get("outstanding", 0)))

        # AP GL is credit-normal (negative debit-credit); sub-ledger outstanding is positive owed.
        difference = gl_balance + subledger_total
        return {
            "ok": difference == 0,
            "controlNominalCode": ap_code,
            "glBalance": str(gl_balance),
            "subledgerBalance": str(subledger_total),
            "difference": str(difference),
            "asOf": as_of.isoformat(),
            "note": "Sub-ledger uses open bill balances minus unallocated payments (AgingService).",
        }
