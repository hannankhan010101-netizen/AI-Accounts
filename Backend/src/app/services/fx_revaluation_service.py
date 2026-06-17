"""Bank FX revaluation — P4."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from app.core.exceptions import ValidationAppError
from app.domain import document_workflow as wf
from app.repositories.bank_repository import BankRepository
from app.repositories.fx_revaluation_repository import FxRevaluationRepository
from app.services.posting_prerequisites_service import PostingPrerequisitesService
from app.services.posting_service import PostingService


class FxRevaluationService:
    def __init__(
        self,
        *,
        fx_repository: FxRevaluationRepository,
        bank_repository: BankRepository,
        posting_service: PostingService,
        prerequisites: PostingPrerequisitesService,
    ) -> None:
        self._fx = fx_repository
        self._banks = bank_repository
        self._posting = posting_service
        self._prereq = prerequisites

    async def list_runs(self, *, company_id: str):
        return await self._fx.list_runs(company_id=company_id)

    async def run_revaluation(
        self,
        *,
        company_id: str,
        bank_account_id: str,
        revaluation_date: datetime,
        foreign_balance: Decimal,
        exchange_rate: Decimal,
        book_balance_base: Decimal | None = None,
    ):
        accounts = await self._banks.list_accounts(company_id=company_id)
        bank = next((a for a in accounts if a.id == bank_account_id), None)
        if bank is None:
            raise ValidationAppError("Bank account not found")
        if not bank.nominalCode:
            raise ValidationAppError("Bank account has no nominal code")

        revalued_base = foreign_balance * exchange_rate
        book = book_balance_base if book_balance_base is not None else Decimal(0)
        gain_loss = revalued_base - book
        if gain_loss == 0:
            raise ValidationAppError("No FX gain or loss to post")

        d = await self._prereq.require_fx_posting(company_id=company_id)
        gain_code = d["fxGainNominalCode"]
        loss_code = d["fxLossNominalCode"]
        bank_code = bank.nominalCode

        if gain_loss > 0:
            lines = [
                {"nominalCode": bank_code, "debit": gain_loss, "credit": Decimal(0)},
                {"nominalCode": gain_code, "debit": Decimal(0), "credit": gain_loss},
            ]
        else:
            amount = abs(gain_loss)
            lines = [
                {"nominalCode": loss_code, "debit": amount, "credit": Decimal(0)},
                {"nominalCode": bank_code, "debit": Decimal(0), "credit": amount},
            ]

        journal = await self._posting.create_traced_journal(
            company_id=company_id,
            journal_date=revaluation_date,
            ref_no=f"FXREV {bank.name}",
            lines=lines,
            source_type=wf.SOURCE_FX_REVALUATION,
            source_id=bank_account_id,
        )
        return await self._fx.create_run(
            company_id=company_id,
            revaluation_date=revaluation_date,
            bank_account_id=bank_account_id,
            foreign_balance=foreign_balance,
            exchange_rate=exchange_rate,
            gain_loss_amount=gain_loss,
            journal_id=journal.id,
        )
