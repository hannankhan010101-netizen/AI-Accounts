"""General journal vouchers."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from app.core.exceptions import ValidationAppError
from app.repositories.sql import journal_queries as jq
from prisma_generated import Prisma
from prisma_generated.models import Journal


def _as_decimal(value: Any) -> Decimal:
    if value is None:
        return Decimal(0)
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


class JournalRepository:
    """Persist manual GL journals and line grids."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def get_by_id(
        self, *, company_id: str, journal_id: str
    ) -> Journal | None:
        row = await self._db.journal.find_unique(
            where={"id": journal_id},
            include={"lines": True},
        )
        if row is None or row.companyId != company_id:
            return None
        return row

    async def lines_for_journal(self, *, journal_id: str):
        return await self._db.journalline.find_many(where={"journalId": journal_id})

    async def mark_reversed(self, *, journal_id: str) -> None:
        await self._db.journal.update(
            where={"id": journal_id},
            data={"status": "reversed"},
        )

    async def assert_mutable(self, *, company_id: str, journal_id: str) -> Journal:
        """Raise when a posted journal must not be edited (P4 immutability)."""

        row = await self.get_by_id(company_id=company_id, journal_id=journal_id)
        if row is None:
            raise ValidationAppError("Journal not found")
        if row.status == "posted" and not row.reversesJournalId:
            raise ValidationAppError(
                "Posted journals are immutable. Reverse the entry instead of editing."
            )
        if row.status == "reversed":
            raise ValidationAppError("Reversed journals cannot be edited")
        return row

    async def update_line(
        self,
        *,
        company_id: str,
        journal_id: str,
        line_id: str,
        data: dict,
    ) -> None:
        await self.assert_mutable(company_id=company_id, journal_id=journal_id)
        line = await self._db.journalline.find_unique(where={"id": line_id})
        if line is None or line.journalId != journal_id:
            raise ValidationAppError("Journal line not found")
        await self._db.journalline.update(where={"id": line_id}, data=data)

    async def list_for_company(
        self,
        *,
        company_id: str,
        take: int = 50,
    ) -> list[Journal]:
        """Return recent journals."""

        return await self._db.journal.find_many(
            where={"companyId": company_id},
            order={"journalDate": "desc"},
            take=take,
        )

    async def trial_balance(
        self,
        *,
        company_id: str,
        as_of_date: datetime | None,
    ) -> list[dict]:
        """
        Aggregate posted journal lines by nominal code, optionally up to ``as_of_date``.

        Returns rows ``{nominalCode, name, debit, credit, balance}`` sorted by
        nominal code; ``name`` is looked up from ``NominalAccount`` filtered to
        this company through the section → category chain.
        """

        if as_of_date is None:
            from app.services.materialized_view_service import MaterializedViewService

            mv_rows = await MaterializedViewService(self._db).trial_balance_from_mv(
                company_id=company_id
            )
            if mv_rows is not None:
                return mv_rows

        raw = await self._db.query_raw(
            jq.TRIAL_BALANCE_SQL,
            company_id,
            as_of_date,
        )
        return [
            {
                "nominalCode": row["nominalCode"],
                "name": row.get("name"),
                "debit": str(_as_decimal(row.get("debit"))),
                "credit": str(_as_decimal(row.get("credit"))),
                "balance": str(_as_decimal(row.get("balance"))),
            }
            for row in raw
        ]

    async def general_ledger(
        self,
        *,
        company_id: str,
        nominal_code: str,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> dict:
        """
        Opening balance, line-by-line activity, and closing balance for one nominal.

        Opening balance = sum of (debit - credit) for posted journals dated strictly
        before ``date_from``. Activity = lines within ``[date_from, date_to]`` inclusive.
        """

        raw = await self._db.query_raw(
            jq.GL_FULL_SQL,
            company_id,
            nominal_code,
            date_from,
            date_to,
            jq.GL_ACTIVITY_MAX_LINES,
        )

        if not raw:
            return {
                "nominalCode": nominal_code,
                "openingBalance": "0",
                "periodDebit": "0",
                "periodCredit": "0",
                "closingBalance": "0",
                "lines": [],
            }

        opening = _as_decimal(raw[0].get("opening"))
        activity_count = int(raw[0].get("activity_count") or 0)
        if activity_count > jq.GL_ACTIVITY_MAX_LINES:
            raise ValidationAppError(
                f"General ledger activity exceeds {jq.GL_ACTIVITY_MAX_LINES} lines; "
                "narrow the date range or use async export."
            )

        activity: list[dict] = []
        period_debit = Decimal(0)
        period_credit = Decimal(0)
        closing = opening
        for row in raw:
            if row.get("line_id") is None:
                continue
            debit = _as_decimal(row.get("debit"))
            credit = _as_decimal(row.get("credit"))
            period_debit += debit
            period_credit += credit
            closing = _as_decimal(row.get("running_balance"))
            journal_date = row.get("journalDate")
            if isinstance(journal_date, datetime):
                journal_date_str = journal_date.isoformat()
            elif journal_date is not None:
                journal_date_str = str(journal_date)
            else:
                journal_date_str = None
            activity.append(
                {
                    "journalId": row.get("journalId"),
                    "journalNumber": row.get("journalNumber"),
                    "journalDate": journal_date_str,
                    "refNo": row.get("refNo"),
                    "projectCode": row.get("projectCode"),
                    "debit": str(debit),
                    "credit": str(credit),
                    "balance": str(closing),
                }
            )

        return {
            "nominalCode": nominal_code,
            "openingBalance": str(opening),
            "periodDebit": str(period_debit),
            "periodCredit": str(period_credit),
            "closingBalance": str(closing),
            "lines": activity,
        }

    async def classified_balances(
        self,
        *,
        company_id: str,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> list[dict]:
        """
        Per-nominal balance over [date_from, date_to] joined with the category
        type so callers can split rows by Income / Expense / Asset / Liability
        / Equity / Other. Category info comes from ``NominalAccount → Section
        → Category``; nominals without a matching master entry are bucketed
        under ``Other`` so unposted-master journals still appear.
        """

        raw = await self._db.query_raw(
            jq.CLASSIFIED_BALANCES_SQL,
            company_id,
            date_from,
            date_to,
        )
        return [
            {
                "nominalCode": row["nominalCode"],
                "name": row.get("name"),
                "categoryType": row.get("categoryType") or "Other",
                "categoryName": row.get("categoryName") or "Uncategorized",
                "debit": str(_as_decimal(row.get("debit"))),
                "credit": str(_as_decimal(row.get("credit"))),
                "balance": str(_as_decimal(row.get("balance"))),
            }
            for row in raw
        ]

    async def monthly_tb_totals(
        self,
        *,
        company_id: str,
        anchor: datetime,
        period_count: int,
    ) -> list[dict]:
        """Cumulative month-end trial balance totals (debit/credit/net) — FIN_TB12."""

        count = min(max(1, period_count), 36)
        raw = await self._db.query_raw(
            jq.MONTHLY_TB_TOTALS_SQL,
            company_id,
            anchor,
            count,
        )
        out: list[dict] = []
        for row in raw:
            total_debit = _as_decimal(row.get("totalDebit"))
            total_credit = _as_decimal(row.get("totalCredit"))
            period_to = row.get("periodTo")
            if hasattr(period_to, "isoformat"):
                period_to_str = period_to.isoformat()
            else:
                period_to_str = str(period_to) if period_to is not None else ""
            out.append(
                {
                    "period": row.get("period"),
                    "periodTo": period_to_str,
                    "accountCount": int(row.get("accountCount") or 0),
                    "totalDebit": str(total_debit),
                    "totalCredit": str(total_credit),
                    "netBalance": str(total_debit - total_credit),
                }
            )
        return out

    async def monthly_classified_pnl(
        self,
        *,
        company_id: str,
        anchor: datetime,
        period_count: int,
    ) -> list[dict]:
        """Monthly income/expense totals — FIN_CMP (single SQL round-trip)."""

        count = min(max(1, period_count), 36)
        raw = await self._db.query_raw(
            jq.MONTHLY_CLASSIFIED_PNL_SQL,
            company_id,
            anchor,
            count,
        )
        out: list[dict] = []
        for row in raw:
            income = _as_decimal(row.get("totalIncome"))
            expense = _as_decimal(row.get("totalExpense"))
            period_from = row.get("periodFrom")
            period_to = row.get("periodTo")
            out.append(
                {
                    "period": row.get("period"),
                    "periodFrom": (
                        period_from.date().isoformat()
                        if hasattr(period_from, "date")
                        else str(period_from)
                    ),
                    "periodTo": (
                        period_to.date().isoformat()
                        if hasattr(period_to, "date")
                        else str(period_to)
                    ),
                    "totalIncome": str(income),
                    "totalExpense": str(expense),
                    "netProfit": str(income - expense),
                }
            )
        return out

    async def monthly_classified_pnl_by_category(
        self,
        *,
        company_id: str,
        anchor: datetime,
        period_count: int,
    ) -> list[dict]:
        """Monthly income/expense by COA category — FIN_PNL_CAT."""

        count = min(max(1, period_count), 36)
        raw = await self._db.query_raw(
            jq.MONTHLY_CLASSIFIED_PNL_BY_CATEGORY_SQL,
            company_id,
            anchor,
            count,
        )
        out: list[dict] = []
        for row in raw:
            ctype = str(row.get("categoryType") or "Other")
            amount = _as_decimal(row.get("amount"))
            if ctype == "Expense":
                amount = -amount
            out.append(
                {
                    "period": row.get("period"),
                    "categoryType": ctype,
                    "categoryName": row.get("categoryName") or "Uncategorized",
                    "amount": str(amount),
                }
            )
        return sorted(
            out,
            key=lambda r: (r["period"], r["categoryType"], -float(r["amount"])),
        )

    async def create_with_lines(
        self,
        *,
        company_id: str,
        journal_number: str,
        journal_date: datetime,
        ref_no: str | None,
        total_amount: Decimal,
        lines: list[dict],
        source_type: str | None = None,
        source_id: str | None = None,
        correlation_id: str | None = None,
        reverses_journal_id: str | None = None,
        journal_id: str | None = None,
        status: str = "posted",
    ) -> Journal:
        """
        Insert a balanced journal header plus child lines.

        Each line dict expects keys: nominalCode, debit, credit, projectCode (optional).
        """

        data: dict[str, Any] = {
                "companyId": company_id,
                "journalNumber": journal_number,
                "journalDate": journal_date,
                "refNo": ref_no,
                "totalAmount": total_amount,
                "status": status,
                "sourceType": source_type,
                "sourceId": source_id,
                "correlationId": correlation_id,
                "reversesJournalId": reverses_journal_id,
                "lines": {"create": lines},
            }
        if journal_id:
            data["id"] = journal_id
        return await self._db.journal.create(
            data=data,
            include={"lines": True},
        )

    async def replace_draft(
        self,
        *,
        company_id: str,
        journal_id: str,
        journal_date: datetime | None,
        ref_no: str | None,
        total_amount: Decimal | None,
        lines: list[dict] | None,
    ) -> Journal:
        row = await self.assert_mutable(company_id=company_id, journal_id=journal_id)
        if row.status != "draft":
            raise ValidationAppError("Only draft journals can be edited")

        header: dict[str, Any] = {}
        if journal_date is not None:
            header["journalDate"] = journal_date
        if ref_no is not None:
            header["refNo"] = ref_no
        if total_amount is not None:
            header["totalAmount"] = total_amount
        if header:
            await self._db.journal.update(where={"id": journal_id}, data=header)

        if lines is not None:
            await self._db.journalline.delete_many(where={"journalId": journal_id})
            if lines:
                await self._db.journalline.create_many(
                    data=[{**line, "journalId": journal_id} for line in lines]
                )

        updated = await self.get_by_id(company_id=company_id, journal_id=journal_id)
        if updated is None:
            raise ValidationAppError("Journal not found")
        return updated

    async def mark_posted(self, *, company_id: str, journal_id: str) -> Journal:
        row = await self.assert_mutable(company_id=company_id, journal_id=journal_id)
        if row.status != "draft":
            raise ValidationAppError("Journal is already posted")
        return await self._db.journal.update(
            where={"id": journal_id},
            data={"status": "posted"},
            include={"lines": True},
        )

    async def delete_journal(self, *, journal_id: str) -> None:
        await self._db.journalline.delete_many(where={"journalId": journal_id})
        await self._db.journal.delete(where={"id": journal_id})
