"""GL posting hooks for operational documents — catalog §9.

Wraps :class:`JournalService` so every operational document creator can post
its own balanced journal in one call. Defaults are sourced from Smart Settings
under the ``defaults`` block:

    payload.defaults.salesNominalCode      # CR for sales invoice
    payload.defaults.receivablesNominalCode # DR for sales invoice
    payload.defaults.purchasesNominalCode  # DR for supplier bill
    payload.defaults.payablesNominalCode   # CR for supplier bill

When any required default is missing the service returns ``None`` and the
caller stores ``journalId = None`` on the document. The TB / GL reports simply
won't see that document until the user back-fills defaults and reposts (post-
back is a follow-up; for now docs created without defaults stay unposted).
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from prisma_generated.models import Journal

from app.domain import document_workflow as wf
from app.repositories.bank_repository import BankRepository
from app.repositories.smart_settings_repository import SmartSettingsRepository
from app.services.journal_service import JournalService
from app.services.tax_calculation_service import TaxLeg


class PostingService:
    """Document → Journal hooks for AR, AP, and Bank movements."""

    def __init__(
        self,
        *,
        journal_service: JournalService,
        smart_settings_repository: SmartSettingsRepository,
        bank_repository: BankRepository,
    ) -> None:
        self._journals = journal_service
        self._smart_settings = smart_settings_repository
        self._banks = bank_repository

    async def _defaults(self, *, company_id: str) -> dict[str, Any]:
        """Return the ``defaults`` block from Smart Settings, or an empty dict."""

        row = await self._smart_settings.get_for_company(company_id=company_id)
        if row is None or not isinstance(row.payload, dict):
            return {}
        defaults = row.payload.get("defaults")
        return defaults if isinstance(defaults, dict) else {}

    async def subledger_nominals(
        self, *, company_id: str
    ) -> tuple[str | None, str | None]:
        """Receivables and payables control nominals from Smart Settings."""

        d = await self._defaults(company_id=company_id)
        ar = d.get("receivablesNominalCode")
        ap = d.get("payablesNominalCode")
        return (
            str(ar) if ar else None,
            str(ap) if ap else None,
        )

    async def create_traced_journal(
        self,
        *,
        company_id: str,
        journal_date: datetime,
        ref_no: str | None,
        lines: list[dict[str, Any]],
        source_type: str,
        source_id: str,
        correlation_id: str,
    ) -> Journal:
        """Balanced journal with source document traceability."""

        return await self._journals.create_journal(
            company_id=company_id,
            journal_date=journal_date,
            ref_no=ref_no,
            lines=lines,
            source_type=source_type,
            source_id=source_id,
            correlation_id=correlation_id,
        )

    async def post_sales_invoice(
        self,
        *,
        company_id: str,
        invoice_date: datetime,
        invoice_number: str,
        net_amount: Decimal,
        gross_amount: Decimal,
        tax_legs: list[TaxLeg] | None = None,
        source_id: str | None = None,
        correlation_id: str | None = None,
    ) -> Journal | None:
        """
        Sales invoice journal: DR receivables (gross), CR sales (net),
        CR GST output per tax leg when configured.
        """

        d = await self._defaults(company_id=company_id)
        ar = d.get("receivablesNominalCode")
        sales = d.get("salesNominalCode")
        gst_output = d.get("gstOutputNominalCode")
        if not ar or not sales:
            return None

        journal_lines: list[dict[str, Any]] = [
            {"nominalCode": ar, "debit": gross_amount, "credit": Decimal(0)},
            {"nominalCode": sales, "debit": Decimal(0), "credit": net_amount},
        ]
        for leg in tax_legs or []:
            if leg.tax_amount <= 0:
                continue
            nominal = leg.nominal_code or gst_output
            if not nominal:
                continue
            journal_lines.append(
                {
                    "nominalCode": nominal,
                    "debit": Decimal(0),
                    "credit": leg.tax_amount,
                }
            )

        return await self._journals.create_journal(
            company_id=company_id,
            journal_date=invoice_date,
            ref_no=f"SI {invoice_number}",
            lines=journal_lines,
            source_type=wf.SOURCE_SALES_INVOICE if source_id else None,
            source_id=source_id,
            correlation_id=correlation_id,
        )

    async def post_sales_credit(
        self,
        *,
        company_id: str,
        credit_date: datetime,
        credit_number: str,
        total_amount: Decimal,
    ) -> Journal | None:
        """Reverses a sales invoice: DR sales / CR receivables."""

        d = await self._defaults(company_id=company_id)
        ar = d.get("receivablesNominalCode")
        sales = d.get("salesNominalCode")
        if not ar or not sales:
            return None

        return await self._journals.create_journal(
            company_id=company_id,
            journal_date=credit_date,
            ref_no=f"SC {credit_number}",
            lines=[
                {"nominalCode": sales, "debit": total_amount, "credit": Decimal(0)},
                {"nominalCode": ar, "debit": Decimal(0), "credit": total_amount},
            ],
        )

    async def post_supplier_credit(
        self,
        *,
        company_id: str,
        credit_date: datetime,
        credit_number: str,
        total_amount: Decimal,
    ) -> Journal | None:
        """Reverses a supplier bill: DR payables / CR purchases."""

        d = await self._defaults(company_id=company_id)
        purchases = d.get("purchasesNominalCode")
        ap = d.get("payablesNominalCode")
        if not purchases or not ap:
            return None

        return await self._journals.create_journal(
            company_id=company_id,
            journal_date=credit_date,
            ref_no=f"VC {credit_number}",
            lines=[
                {"nominalCode": ap, "debit": total_amount, "credit": Decimal(0)},
                {"nominalCode": purchases, "debit": Decimal(0), "credit": total_amount},
            ],
        )

    async def post_supplier_bill(
        self,
        *,
        company_id: str,
        bill_date: datetime,
        bill_number: str,
        net_amount: Decimal,
        gross_amount: Decimal,
        tax_legs: list[TaxLeg] | None = None,
        source_id: str | None = None,
        correlation_id: str | None = None,
    ) -> Journal | None:
        """Supplier bill: DR purchases (net), DR GST input (tax), CR payables (gross)."""

        d = await self._defaults(company_id=company_id)
        purchases = d.get("purchasesNominalCode")
        ap = d.get("payablesNominalCode")
        gst_input = d.get("gstInputNominalCode")
        if not purchases or not ap:
            return None

        journal_lines: list[dict[str, Any]] = [
            {"nominalCode": purchases, "debit": net_amount, "credit": Decimal(0)},
            {"nominalCode": ap, "debit": Decimal(0), "credit": gross_amount},
        ]
        for leg in tax_legs or []:
            if leg.tax_amount <= 0:
                continue
            nominal = leg.nominal_code or gst_input
            if not nominal:
                continue
            journal_lines.append(
                {
                    "nominalCode": nominal,
                    "debit": leg.tax_amount,
                    "credit": Decimal(0),
                }
            )

        return await self._journals.create_journal(
            company_id=company_id,
            journal_date=bill_date,
            ref_no=f"VI {bill_number}",
            lines=journal_lines,
            source_type=wf.SOURCE_SUPPLIER_BILL if source_id else None,
            source_id=source_id,
            correlation_id=correlation_id,
        )

    async def post_sales_receipt(
        self,
        *,
        company_id: str,
        receipt_date: datetime,
        receipt_number: str,
        bank_account_id: str,
        total_amount: Decimal,
        wht_amount: Decimal | None = None,
        wht_nominal_code: str | None = None,
    ) -> Journal | None:
        """DR bank (net), optional DR WHT, CR receivables (gross)."""

        d = await self._defaults(company_id=company_id)
        ar = d.get("receivablesNominalCode")
        if not ar:
            return None

        accounts = await self._banks.list_accounts(company_id=company_id)
        bank = next((a for a in accounts if a.id == bank_account_id), None)
        if bank is None or not bank.nominalCode:
            return None

        wht = wht_amount or Decimal(0)
        gross = total_amount + wht
        lines: list[dict] = [
            {"nominalCode": bank.nominalCode, "debit": total_amount, "credit": Decimal(0)},
        ]
        if wht > 0 and wht_nominal_code:
            lines.append(
                {"nominalCode": wht_nominal_code, "debit": wht, "credit": Decimal(0)}
            )
        lines.append({"nominalCode": ar, "debit": Decimal(0), "credit": gross})

        return await self._journals.create_journal(
            company_id=company_id,
            journal_date=receipt_date,
            ref_no=f"SR {receipt_number}",
            lines=lines,
        )

    async def post_supplier_payment(
        self,
        *,
        company_id: str,
        payment_date: datetime,
        voucher_number: str,
        bank_account_id: str,
        total_amount: Decimal,
        wht_amount: Decimal | None = None,
        wht_nominal_code: str | None = None,
    ) -> Journal | None:
        """DR payables (gross), CR bank (net), optional CR WHT payable."""

        d = await self._defaults(company_id=company_id)
        ap = d.get("payablesNominalCode")
        if not ap:
            return None

        accounts = await self._banks.list_accounts(company_id=company_id)
        bank = next((a for a in accounts if a.id == bank_account_id), None)
        if bank is None or not bank.nominalCode:
            return None

        wht = wht_amount or Decimal(0)
        gross = total_amount + wht
        lines: list[dict] = [
            {"nominalCode": ap, "debit": gross, "credit": Decimal(0)},
            {"nominalCode": bank.nominalCode, "debit": Decimal(0), "credit": total_amount},
        ]
        if wht > 0 and wht_nominal_code:
            lines.append(
                {"nominalCode": wht_nominal_code, "debit": Decimal(0), "credit": wht}
            )

        return await self._journals.create_journal(
            company_id=company_id,
            journal_date=payment_date,
            ref_no=f"VP {voucher_number}",
            lines=lines,
        )

    async def post_bank_receipt(
        self,
        *,
        company_id: str,
        receipt_date: datetime,
        voucher_number: str,
        bank_account_id: str,
        counterpart_nominal_code: str | None,
        total_amount: Decimal,
    ) -> Journal | None:
        """DR bank, CR counterpart. Skipped when either nominal is missing."""

        if not counterpart_nominal_code:
            return None

        accounts = await self._banks.list_accounts(company_id=company_id)
        bank = next((a for a in accounts if a.id == bank_account_id), None)
        if bank is None or not bank.nominalCode:
            return None

        return await self._journals.create_journal(
            company_id=company_id,
            journal_date=receipt_date,
            ref_no=f"IR {voucher_number}",
            lines=[
                {"nominalCode": bank.nominalCode, "debit": total_amount, "credit": Decimal(0)},
                {
                    "nominalCode": counterpart_nominal_code,
                    "debit": Decimal(0),
                    "credit": total_amount,
                },
            ],
        )

    async def post_bank_transfer(
        self,
        *,
        company_id: str,
        transfer_date: datetime,
        voucher_number: str,
        from_bank_account_id: str,
        to_bank_account_id: str,
        total_amount: Decimal,
    ) -> Journal | None:
        """DR to-bank, CR from-bank. Skipped when either nominal is missing."""

        accounts = await self._banks.list_accounts(company_id=company_id)
        from_bank = next((a for a in accounts if a.id == from_bank_account_id), None)
        to_bank = next((a for a in accounts if a.id == to_bank_account_id), None)
        if (
            from_bank is None
            or to_bank is None
            or not from_bank.nominalCode
            or not to_bank.nominalCode
        ):
            return None

        return await self._journals.create_journal(
            company_id=company_id,
            journal_date=transfer_date,
            ref_no=f"BT {voucher_number}",
            lines=[
                {"nominalCode": to_bank.nominalCode, "debit": total_amount, "credit": Decimal(0)},
                {
                    "nominalCode": from_bank.nominalCode,
                    "debit": Decimal(0),
                    "credit": total_amount,
                },
            ],
        )

    async def post_bank_payment(
        self,
        *,
        company_id: str,
        payment_date: datetime,
        voucher_number: str,
        bank_account_id: str,
        counterpart_nominal_code: str | None,
        total_amount: Decimal,
    ) -> Journal | None:
        """
        Two-line journal: DR counterpart (expense or AP code chosen at create
        time), CR bank account's nominal. Skipped silently when either nominal
        is missing — the document is recorded but unposted.
        """

        if not counterpart_nominal_code:
            return None

        accounts = await self._banks.list_accounts(company_id=company_id)
        bank = next((a for a in accounts if a.id == bank_account_id), None)
        if bank is None or not bank.nominalCode:
            return None

        return await self._journals.create_journal(
            company_id=company_id,
            journal_date=payment_date,
            ref_no=f"EP {voucher_number}",
            lines=[
                {
                    "nominalCode": counterpart_nominal_code,
                    "debit": total_amount,
                    "credit": Decimal(0),
                },
                {
                    "nominalCode": bank.nominalCode,
                    "debit": Decimal(0),
                    "credit": total_amount,
                },
            ],
        )

    async def post_bank_payment_split(
        self,
        *,
        company_id: str,
        payment_date: datetime,
        voucher_number: str,
        bank_account_id: str,
        nominal_lines: list[tuple[str, Decimal]],
    ) -> Journal | None:
        """Multi-line DR nominals + single CR bank line."""

        if not nominal_lines:
            return None

        accounts = await self._banks.list_accounts(company_id=company_id)
        bank = next((a for a in accounts if a.id == bank_account_id), None)
        if bank is None or not bank.nominalCode:
            return None

        total = sum((amt for _, amt in nominal_lines), Decimal(0))
        if total <= 0:
            return None

        journal_lines: list[dict] = [
            {
                "nominalCode": code,
                "debit": amt,
                "credit": Decimal(0),
            }
            for code, amt in nominal_lines
            if code and amt > 0
        ]
        journal_lines.append(
            {
                "nominalCode": bank.nominalCode,
                "debit": Decimal(0),
                "credit": total,
            }
        )
        return await self._journals.create_journal(
            company_id=company_id,
            journal_date=payment_date,
            ref_no=f"EP {voucher_number}",
            lines=journal_lines,
        )
