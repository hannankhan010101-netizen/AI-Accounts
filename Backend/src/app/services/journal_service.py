"""General journal posting orchestration (minimal balanced check)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from app.core.exceptions import ValidationAppError
from prisma_generated.models import Journal

from app.repositories.coa_repository import CoaRepository
from app.repositories.journal_repository import JournalRepository
from app.services.document_number_service import DocumentNumberService
from app.services.lock_date_service import LockDateService


class JournalService:
    """Creates journals and reserves voucher numbers."""

    def __init__(
        self,
        *,
        journal_repository: JournalRepository,
        document_number_service: DocumentNumberService,
        coa_repository: CoaRepository | None = None,
        lock_date_service: LockDateService | None = None,
    ) -> None:
        self._journals = journal_repository
        self._numbers = document_number_service
        self._coa = coa_repository
        self._lock_date = lock_date_service

    async def list_journals(self, *, company_id: str):
        """Return recent journal vouchers."""

        return await self._journals.list_for_company(company_id=company_id)

    async def create_journal(
        self,
        *,
        company_id: str,
        journal_date: datetime,
        ref_no: str | None,
        lines: list[dict],
        source_type: str | None = None,
        source_id: str | None = None,
        correlation_id: str | None = None,
        reverses_journal_id: str | None = None,
        journal_id: str | None = None,
        status: str = "posted",
    ):
        """
        Persist a journal after verifying debits equal credits.

        ``lines`` use Prisma keys: nominalCode, debit, credit, projectCode (optional).
        """

        if self._lock_date is not None and status != "draft":
            await self._lock_date.assert_not_locked(
                company_id=company_id,
                document_date=journal_date,
                document_label="journal",
            )

        total_debit = sum(Decimal(str(line.get("debit", 0))) for line in lines)
        total_credit = sum(Decimal(str(line.get("credit", 0))) for line in lines)
        if total_debit != total_credit:
            raise ValidationAppError("Journal lines are not balanced")
        enriched = await self._enrich_lines(company_id=company_id, lines=lines)
        journal_number = str(
            await self._numbers.reserve_next(company_id=company_id, sequence_key="journal")
        )
        row = await self._journals.create_with_lines(
            company_id=company_id,
            journal_number=journal_number,
            journal_date=journal_date,
            ref_no=ref_no,
            total_amount=total_debit,
            lines=enriched,
            source_type=source_type,
            source_id=source_id,
            correlation_id=correlation_id,
            reverses_journal_id=reverses_journal_id,
            journal_id=journal_id,
            status=status,
        )
        if status == "posted":
            from app.core.report_cache import get_report_cache

            await get_report_cache().bump_version(company_id=company_id)
        return row

    async def _enrich_lines(
        self, *, company_id: str, lines: list[dict]
    ) -> list[dict]:
        if self._coa is None:
            return lines
        codes = [str(line["nominalCode"]) for line in lines if line.get("nominalCode")]
        id_map = await self._coa.nominal_ids_by_codes(
            company_id=company_id, codes=codes
        )
        out: list[dict] = []
        for line in lines:
            row = dict(line)
            code = str(row.get("nominalCode", ""))
            nid = id_map.get(code)
            if nid:
                row["nominalAccountId"] = nid
            out.append(row)
        return out

    async def get_journal(self, *, company_id: str, journal_id: str) -> Journal | None:
        return await self._journals.get_by_id(
            company_id=company_id, journal_id=journal_id
        )

    async def reverse_journal(
        self,
        *,
        company_id: str,
        journal_id: str,
        reversal_date: datetime,
        ref_no: str | None = None,
    ) -> Journal:
        """Create a storno entry; original journal remains posted (immutable)."""

        original = await self._journals.get_by_id(
            company_id=company_id, journal_id=journal_id
        )
        if original is None:
            raise ValidationAppError("Journal not found")
        if original.status == "reversed":
            raise ValidationAppError("Journal was already reversed")
        if original.reversesJournalId:
            raise ValidationAppError("Cannot reverse a reversal entry")

        lines = await self._journals.lines_for_journal(journal_id=journal_id)
        reversal_lines = [
            {
                "nominalCode": line.nominalCode,
                "debit": line.credit,
                "credit": line.debit,
                "projectCode": line.projectCode,
            }
            for line in lines
        ]
        rev = await self.create_journal(
            company_id=company_id,
            journal_date=reversal_date,
            ref_no=ref_no or f"REV {original.journalNumber}",
            lines=reversal_lines,
            source_type="JOURNAL_REVERSAL",
            source_id=journal_id,
            reverses_journal_id=journal_id,
        )
        await self._journals.mark_reversed(journal_id=journal_id)
        return rev

    async def copy_journal(
        self,
        *,
        company_id: str,
        journal_id: str,
        journal_date: datetime | None = None,
    ) -> Journal:
        """Clone a journal with a new number (FA copy action)."""

        original = await self._journals.get_by_id(
            company_id=company_id, journal_id=journal_id
        )
        if original is None:
            raise ValidationAppError("Journal not found")
        lines = await self._journals.lines_for_journal(journal_id=journal_id)
        copy_lines = [
            {
                "nominalCode": line.nominalCode,
                "debit": line.debit,
                "credit": line.credit,
                "projectCode": line.projectCode,
            }
            for line in lines
        ]
        ref = original.refNo or original.journalNumber
        return await self.create_journal(
            company_id=company_id,
            journal_date=journal_date or original.journalDate,
            ref_no=f"COPY OF {ref}" if ref else "COPY",
            lines=copy_lines,
        )

    async def update_draft(
        self,
        *,
        company_id: str,
        journal_id: str,
        journal_date: datetime | None = None,
        ref_no: str | None = None,
        lines: list[dict] | None = None,
    ) -> Journal:
        """Replace header/lines on a draft journal."""

        enriched = (
            await self._enrich_lines(company_id=company_id, lines=lines)
            if lines is not None
            else None
        )
        total_amount = None
        if enriched is not None:
            total_debit = sum(Decimal(str(line.get("debit", 0))) for line in enriched)
            total_credit = sum(Decimal(str(line.get("credit", 0))) for line in enriched)
            if total_debit != total_credit:
                raise ValidationAppError("Journal lines are not balanced")
            total_amount = total_debit
        return await self._journals.replace_draft(
            company_id=company_id,
            journal_id=journal_id,
            journal_date=journal_date,
            ref_no=ref_no,
            total_amount=total_amount,
            lines=enriched,
        )

    async def bulk_delete_drafts(
        self, *, company_id: str, journal_ids: list[str]
    ) -> dict[str, int]:
        """Delete manual draft journals only (no source document)."""

        deleted = 0
        skipped = 0
        for journal_id in journal_ids:
            row = await self._journals.get_by_id(
                company_id=company_id, journal_id=journal_id
            )
            if row is None or row.status != "draft" or row.sourceType:
                skipped += 1
                continue
            await self._journals.delete_journal(journal_id=journal_id)
            deleted += 1
        return {"deleted": deleted, "skipped": skipped}

    async def post_draft(
        self,
        *,
        company_id: str,
        journal_id: str,
    ) -> Journal:
        """Post a balanced draft journal to the GL."""

        row = await self._journals.get_by_id(company_id=company_id, journal_id=journal_id)
        if row is None:
            raise ValidationAppError("Journal not found")
        if row.status != "draft":
            raise ValidationAppError("Only draft journals can be posted")

        lines = await self._journals.lines_for_journal(journal_id=journal_id)
        total_debit = sum(line.debit for line in lines)
        total_credit = sum(line.credit for line in lines)
        if total_debit != total_credit or total_debit <= 0:
            raise ValidationAppError("Journal lines are not balanced")

        if self._lock_date is not None:
            await self._lock_date.assert_not_locked(
                company_id=company_id,
                document_date=row.journalDate,
                document_label="journal",
            )
        return await self._journals.mark_posted(
            company_id=company_id, journal_id=journal_id
        )
