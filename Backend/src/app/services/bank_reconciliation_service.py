"""Bank reconciliation orchestration — catalog §4.5."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from prisma_generated import Prisma
from prisma_generated.models import BankReconciliation

from app.core.exceptions import ValidationAppError
from app.repositories.bank_reconciliation_repository import BankReconciliationRepository
from app.repositories.bank_repository import BankRepository


class BankReconciliationService:
    def __init__(
        self,
        *,
        prisma: Prisma,
        reconciliation_repository: BankReconciliationRepository,
        bank_repository: BankRepository,
    ) -> None:
        self._db = prisma
        self._recon = reconciliation_repository
        self._banks = bank_repository

    async def _load_bank_movements(
        self, *, company_id: str, bank_account_id: str, through_date: datetime
    ) -> list[dict]:
        items: list[dict] = []

        payments = await self._db.bankpayment.find_many(
            where={
                "companyId": company_id,
                "bankAccountId": bank_account_id,
                "paymentDate": {"lte": through_date},
            },
            take=5000,
        )
        for p in payments:
            items.append(
                {
                    "itemType": "bank_payment",
                    "itemId": p.id,
                    "transactionDate": p.paymentDate,
                    "amount": -p.totalAmount,
                    "reference": p.voucherNumber,
                }
            )

        receipts = await self._db.bankreceipt.find_many(
            where={
                "companyId": company_id,
                "bankAccountId": bank_account_id,
                "receiptDate": {"lte": through_date},
            },
            take=5000,
        )
        for r in receipts:
            items.append(
                {
                    "itemType": "bank_receipt",
                    "itemId": r.id,
                    "transactionDate": r.receiptDate,
                    "amount": r.totalAmount,
                    "reference": r.voucherNumber,
                }
            )

        transfers = await self._db.banktransfer.find_many(
            where={
                "companyId": company_id,
                "OR": [
                    {"fromBankAccountId": bank_account_id},
                    {"toBankAccountId": bank_account_id},
                ],
                "transferDate": {"lte": through_date},
            },
            take=5000,
        )
        for t in transfers:
            if t.fromBankAccountId == bank_account_id:
                items.append(
                    {
                        "itemType": "bank_transfer",
                        "itemId": t.id,
                        "transactionDate": t.transferDate,
                        "amount": -t.totalAmount,
                        "reference": t.voucherNumber,
                    }
                )
            else:
                items.append(
                    {
                        "itemType": "bank_transfer",
                        "itemId": t.id,
                        "transactionDate": t.transferDate,
                        "amount": t.totalAmount,
                        "reference": t.voucherNumber,
                    }
                )
        return items

    async def _mark_cleared_documents(
        self, *, company_id: str, items: list
    ) -> None:
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        for item in items:
            if item.itemType == "statement_line":
                continue
            data = {"reconciledAt": now}
            if item.itemType == "bank_payment":
                await self._db.bankpayment.update_many(
                    where={"id": item.itemId, "companyId": company_id},
                    data=data,
                )
            elif item.itemType == "bank_receipt":
                await self._db.bankreceipt.update_many(
                    where={"id": item.itemId, "companyId": company_id},
                    data=data,
                )
            elif item.itemType == "bank_transfer":
                await self._db.banktransfer.update_many(
                    where={"id": item.itemId, "companyId": company_id},
                    data=data,
                )

    async def list_sessions(
        self, *, company_id: str, bank_account_id: str | None = None
    ) -> list[BankReconciliation]:
        return await self._recon.list_sessions(
            company_id=company_id, bank_account_id=bank_account_id
        )

    async def get_session(
        self, *, company_id: str, reconciliation_id: str
    ) -> BankReconciliation | None:
        return await self._recon.get_session(
            company_id=company_id, reconciliation_id=reconciliation_id
        )

    async def start_reconciliation(
        self,
        *,
        company_id: str,
        bank_account_id: str,
        statement_date: datetime,
        statement_balance: Decimal,
        notes: str | None,
    ) -> BankReconciliation:
        accounts = await self._banks.list_accounts(company_id=company_id)
        if not any(a.id == bank_account_id for a in accounts):
            raise ValidationAppError("Bank account not found")

        items = await self._load_bank_movements(
            company_id=company_id,
            bank_account_id=bank_account_id,
            through_date=statement_date,
        )
        return await self._recon.create_session(
            company_id=company_id,
            bank_account_id=bank_account_id,
            statement_date=statement_date,
            statement_balance=statement_balance,
            notes=notes,
            items=items,
        )

    async def update_cleared_items(
        self,
        *,
        company_id: str,
        reconciliation_id: str,
        item_ids: list[str],
        cleared: bool,
    ) -> BankReconciliation:
        session = await self._recon.get_session(
            company_id=company_id, reconciliation_id=reconciliation_id
        )
        if session is None:
            raise ValidationAppError("Reconciliation session not found")
        if session.status != "open":
            raise ValidationAppError("Reconciliation is already completed")
        await self._recon.set_items_cleared(
            reconciliation_id=reconciliation_id,
            item_ids=item_ids,
            cleared=cleared,
        )
        return await self._recon.get_session(
            company_id=company_id, reconciliation_id=reconciliation_id
        )  # type: ignore[return-value]

    async def auto_match_items(
        self,
        *,
        company_id: str,
        reconciliation_id: str,
    ) -> BankReconciliation:
        """Pair statement lines with ledger movements by absolute amount."""

        session = await self._recon.get_session(
            company_id=company_id, reconciliation_id=reconciliation_id
        )
        if session is None:
            raise ValidationAppError("Reconciliation session not found")
        if session.status != "open":
            raise ValidationAppError("Reconciliation is already completed")

        items = session.items or []
        ledger = [i for i in items if i.itemType != "statement_line" and not i.isCleared]
        statements = [
            i for i in items if i.itemType == "statement_line" and not i.isCleared
        ]
        to_clear: list[str] = []
        used_ledger: set[str] = set()

        for stmt in statements:
            stmt_amt = abs(Decimal(str(stmt.amount)))
            for led in ledger:
                if led.id in used_ledger:
                    continue
                if abs(Decimal(str(led.amount))) == stmt_amt:
                    to_clear.extend([stmt.id, led.id])
                    used_ledger.add(led.id)
                    break

        if to_clear:
            await self._recon.set_items_cleared(
                reconciliation_id=reconciliation_id,
                item_ids=to_clear,
                cleared=True,
            )
        return await self._recon.get_session(
            company_id=company_id, reconciliation_id=reconciliation_id
        )  # type: ignore[return-value]

    async def complete_reconciliation(
        self,
        *,
        company_id: str,
        reconciliation_id: str,
    ) -> dict:
        session = await self._recon.get_session(
            company_id=company_id, reconciliation_id=reconciliation_id
        )
        if session is None:
            raise ValidationAppError("Reconciliation session not found")
        if session.status != "open":
            raise ValidationAppError("Reconciliation is already completed")

        cleared_total = Decimal(0)
        for item in session.items or []:
            if item.isCleared:
                cleared_total += item.amount

        difference = session.statementBalance - cleared_total
        status = "completed" if difference == 0 else "completed_with_variance"
        updated = await self._recon.complete_session(
            reconciliation_id=reconciliation_id, status=status
        )
        await self._mark_cleared_documents(
            company_id=company_id,
            items=[i for i in (session.items or []) if i.isCleared],
        )
        return {
            "session": updated,
            "clearedTotal": str(cleared_total),
            "statementBalance": str(session.statementBalance),
            "difference": str(difference),
            "balanced": difference == 0,
        }

    async def import_statement(
        self,
        *,
        company_id: str,
        bank_account_id: str,
        statement_date: datetime,
        statement_balance: Decimal | None,
        rows: list[dict],
        notes: str | None = None,
    ) -> BankReconciliation:
        """Parse bank statement rows and open a reconciliation session (catalog §4.5a)."""

        from uuid import uuid4

        accounts = await self._banks.list_accounts(company_id=company_id)
        if not any(a.id == bank_account_id for a in accounts):
            raise ValidationAppError("Bank account not found")
        if not rows:
            raise ValidationAppError("Statement file has no data rows")

        statement_items: list[dict] = []
        running = Decimal(0)
        for i, row in enumerate(rows):
            amount = _parse_statement_amount(row)
            tx_date = _parse_statement_date(row, fallback=statement_date)
            ref = _statement_reference(row, i)
            statement_items.append(
                {
                    "itemType": "statement_line",
                    "itemId": f"stmt-{i}-{uuid4().hex[:10]}",
                    "transactionDate": tx_date,
                    "amount": amount,
                    "reference": ref,
                }
            )
            running += amount

        balance = statement_balance if statement_balance is not None else running
        ledger_items = await self._load_bank_movements(
            company_id=company_id,
            bank_account_id=bank_account_id,
            through_date=statement_date,
        )
        import_note = notes or f"Imported {len(statement_items)} statement line(s)"
        return await self._recon.create_session(
            company_id=company_id,
            bank_account_id=bank_account_id,
            statement_date=statement_date,
            statement_balance=balance,
            notes=import_note,
            items=[*ledger_items, *statement_items],
        )


def _parse_statement_amount(row: dict) -> Decimal:
    for key in ("amount", "Amount", "Bank Amount", "Debit", "Credit", "Value"):
        if key in row and str(row[key]).strip():
            raw = str(row[key]).replace(",", "").strip()
            try:
                return Decimal(raw)
            except Exception:
                continue
    debit = str(row.get("Debit") or row.get("debit") or "").replace(",", "").strip()
    credit = str(row.get("Credit") or row.get("credit") or "").replace(",", "").strip()
    if debit:
        try:
            return -abs(Decimal(debit))
        except Exception:
            pass
    if credit:
        try:
            return abs(Decimal(credit))
        except Exception:
            pass
    return Decimal(0)


def _parse_statement_date(row: dict, *, fallback: datetime) -> datetime:
    for key in ("date", "Date", "Transaction Date", "Payment Date", "Value Date"):
        val = row.get(key)
        if val is None or str(val).strip() == "":
            continue
        if isinstance(val, datetime):
            return val
        s = str(val).strip()
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"):
            try:
                return datetime.strptime(s, fmt).replace(tzinfo=fallback.tzinfo)
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(s.replace("Z", "+00:00"))
        except ValueError:
            continue
    return fallback


def _statement_reference(row: dict, index: int) -> str:
    for key in ("description", "Description", "Notes", "Ref No", "Reference", "Narration"):
        val = str(row.get(key) or "").strip()
        if val:
            return val[:200]
    return f"Statement line {index + 1}"
