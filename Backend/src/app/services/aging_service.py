"""AR / AP aging + per-party statement aggregation — catalog §10.7, §10.9, §5.9.

Pre-allocation model: each invoice / bill contributes its full ``totalAmount`` to
the open balance; each receipt / payment subtracts. Aging is bucketed off the
oldest *open* invoice/bill per party (a single-bucket approximation until
per-document allocation lands in Phase 4.6 / 5.4).

Buckets follow the catalog §10.9 dashboard wording exactly:
``Older``, ``Current``, ``1–7 days``, ``8–14 days``, ``15–21 days``,
``22–28 days``, ``Future``.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from functools import partial
from typing import Any

from prisma_generated import Prisma

from app.core.async_io import maybe_thread
from app.repositories.sql import aging_queries as aq


BUCKETS = ["Older", "Current", "1-7", "8-14", "15-21", "22-28", "Future"]


def bucket_for(age_days: int) -> str:
    """Map age-in-days to a bucket label."""

    if age_days < 0:
        return "Future"
    if age_days == 0:
        return "Current"
    if age_days <= 7:
        return "1-7"
    if age_days <= 14:
        return "8-14"
    if age_days <= 21:
        return "15-21"
    if age_days <= 28:
        return "22-28"
    return "Older"


def _to_utc(value: Any) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    return datetime.fromisoformat(str(value)).astimezone(timezone.utc)


class AgingService:
    """AR/AP aging and statement queries."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def ar_aging(
        self,
        *,
        company_id: str,
        as_of_date: datetime | None,
    ) -> dict[str, Any]:
        """Per-customer open balance bucketed by oldest *open* invoice age."""

        as_of = _to_utc(as_of_date) if as_of_date else datetime.now(timezone.utc)
        rows = await self._fetch_ar_rows(company_id=company_id, as_of=as_of)
        return await maybe_thread(
            partial(AgingService._summarize_from_sql_rows, rows, as_of, party_kind="customer"),
            min_rows=500,
            row_count=len(rows),
        )

    async def ap_aging(
        self,
        *,
        company_id: str,
        as_of_date: datetime | None,
    ) -> dict[str, Any]:
        """Per-supplier open balance bucketed by oldest *open* bill age."""

        as_of = _to_utc(as_of_date) if as_of_date else datetime.now(timezone.utc)
        rows = await self._fetch_ap_rows(company_id=company_id, as_of=as_of)
        return await maybe_thread(
            partial(AgingService._summarize_from_sql_rows, rows, as_of, party_kind="supplier"),
            min_rows=500,
            row_count=len(rows),
        )

    async def _fetch_ar_rows(
        self, *, company_id: str, as_of: datetime
    ) -> list[dict[str, Any]]:
        if as_of_date_is_current(as_of):
            try:
                raw = await self._db.query_raw(
                    aq.AR_AGING_FROM_MV_MERGED_SQL, company_id
                )
                return [dict(r) for r in raw]
            except Exception:  # noqa: BLE001
                pass
        raw = await self._db.query_raw(
            aq.AR_AGING_MERGED_SQL, company_id, as_of
        )
        return [dict(r) for r in raw]

    async def _fetch_ap_rows(
        self, *, company_id: str, as_of: datetime
    ) -> list[dict[str, Any]]:
        if as_of_date_is_current(as_of):
            try:
                raw = await self._db.query_raw(
                    aq.AP_AGING_FROM_MV_MERGED_SQL, company_id
                )
                return [dict(r) for r in raw]
            except Exception:  # noqa: BLE001
                pass
        raw = await self._db.query_raw(
            aq.AP_AGING_MERGED_SQL, company_id, as_of
        )
        return [dict(r) for r in raw]

    @staticmethod
    def _summarize_from_sql_rows(
        rows: list[dict[str, Any]],
        as_of: datetime,
        *,
        party_kind: str,
    ) -> dict[str, Any]:
        result_rows: list[dict[str, Any]] = []
        bucket_totals = {b: Decimal(0) for b in BUCKETS}
        bucket_counts = {b: 0 for b in BUCKETS}
        grand_total = Decimal(0)

        for row in rows:
            party_id = row.get("partyId")
            balance = Decimal(str(row.get("remaining") or 0))
            oldest_raw = row.get("oldestOpenDate")
            oldest = _to_utc(oldest_raw) if oldest_raw is not None else None

            if balance == 0 and oldest is None:
                continue

            age_days = (as_of - oldest).days if oldest else 0
            bucket = bucket_for(age_days)

            result_rows.append(
                {
                    "partyId": party_id,
                    "partyName": row.get("partyName"),
                    "partyCode": row.get("partyCode"),
                    "kind": party_kind,
                    "invoicesTotal": str(row.get("invoicesTotal") or 0),
                    "receiptsTotal": str(row.get("receiptsTotal") or 0),
                    "openInvoiceCount": int(row.get("openInvoiceCount") or 0),
                    "balance": str(balance),
                    "oldestDate": oldest.isoformat() if oldest else None,
                    "ageDays": age_days,
                    "bucket": bucket,
                }
            )

            if balance > 0:
                bucket_totals[bucket] += balance
                bucket_counts[bucket] += 1
                grand_total += balance

        result_rows.sort(key=lambda r: Decimal(r["balance"]), reverse=True)

        return {
            "asOfDate": as_of.date().isoformat(),
            "rows": result_rows,
            "buckets": [
                {
                    "label": b,
                    "total": str(bucket_totals[b]),
                    "count": bucket_counts[b],
                }
                for b in BUCKETS
            ],
            "totals": {
                "outstanding": str(grand_total),
                "partyCount": len([r for r in result_rows if Decimal(r["balance"]) > 0]),
            },
        }

    async def customer_statement(
        self,
        *,
        company_id: str,
        customer_id: str,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> dict[str, Any]:
        """Chronological invoice + receipt list with running balance."""

        inv_where = self._date_filter(
            {"companyId": company_id, "customerId": customer_id},
            "invoiceDate",
            date_from,
            date_to,
        )
        rec_where = self._date_filter(
            {"companyId": company_id, "customerId": customer_id},
            "receiptDate",
            date_from,
            date_to,
        )
        invoices, receipts = await asyncio.gather(
            self._db.salesinvoice.find_many(where=inv_where, take=100_000),
            self._db.salesreceipt.find_many(where=rec_where, take=100_000),
        )
        return await maybe_thread(
            _build_customer_statement,
            invoices,
            receipts,
            customer_id,
            min_rows=1000,
            row_count=len(invoices) + len(receipts),
        )

    async def supplier_statement(
        self,
        *,
        company_id: str,
        supplier_id: str,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> dict[str, Any]:
        """Bills (CR) + payments (DR) for a supplier with running balance."""

        bill_where = self._date_filter(
            {"companyId": company_id, "supplierId": supplier_id},
            "billDate",
            date_from,
            date_to,
        )
        pay_where = self._date_filter(
            {"companyId": company_id, "supplierId": supplier_id},
            "paymentDate",
            date_from,
            date_to,
        )
        bills, payments = await asyncio.gather(
            self._db.supplierbill.find_many(where=bill_where, take=100_000),
            self._db.supplierpayment.find_many(where=pay_where, take=100_000),
        )
        return await maybe_thread(
            _build_supplier_statement,
            bills,
            payments,
            supplier_id,
            min_rows=1000,
            row_count=len(bills) + len(payments),
        )

    @staticmethod
    def _date_filter(
        base: dict[str, Any],
        field: str,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> dict[str, Any]:
        if date_from is None and date_to is None:
            return base
        rng: dict[str, Any] = {}
        if date_from:
            rng["gte"] = date_from
        if date_to:
            rng["lte"] = date_to
        return {**base, field: rng}


def _build_customer_statement(
    invoices: list[Any],
    receipts: list[Any],
    customer_id: str,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for inv in invoices:
        rows.append(
            {
                "date": _to_utc(inv.invoiceDate).isoformat(),
                "kind": "invoice",
                "reference": inv.invoiceNumber,
                "debit": str(inv.totalAmount),
                "credit": "0",
                "id": inv.id,
            }
        )
    for rec in receipts:
        rows.append(
            {
                "date": _to_utc(rec.receiptDate).isoformat(),
                "kind": "receipt",
                "reference": rec.receiptNumber,
                "debit": "0",
                "credit": str(rec.totalAmount),
                "id": rec.id,
            }
        )
    rows.sort(key=lambda r: r["date"])

    running = Decimal(0)
    total_debit = Decimal(0)
    total_credit = Decimal(0)
    for row in rows:
        d = Decimal(row["debit"])
        c = Decimal(row["credit"])
        running += d - c
        total_debit += d
        total_credit += c
        row["balance"] = str(running)

    party_code = None
    party_name = None
    for inv in invoices:
        if inv.customerCode or inv.customerName:
            party_code = inv.customerCode
            party_name = inv.customerName
            break
    if party_name is None:
        for rec in receipts:
            if rec.customerCode or rec.customerName:
                party_code = rec.customerCode
                party_name = rec.customerName
                break

    return {
        "party": {"id": customer_id, "name": party_name, "code": party_code},
        "lines": rows,
        "totals": {
            "debit": str(total_debit),
            "credit": str(total_credit),
            "balance": str(running),
        },
    }


def _build_supplier_statement(
    bills: list[Any],
    payments: list[Any],
    supplier_id: str,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for bill in bills:
        rows.append(
            {
                "date": _to_utc(bill.billDate).isoformat(),
                "kind": "bill",
                "reference": bill.billNumber,
                "debit": "0",
                "credit": str(bill.totalAmount),
                "id": bill.id,
            }
        )
    for pay in payments:
        rows.append(
            {
                "date": _to_utc(pay.paymentDate).isoformat(),
                "kind": "payment",
                "reference": pay.voucherNumber,
                "debit": str(pay.totalAmount),
                "credit": "0",
                "id": pay.id,
            }
        )
    rows.sort(key=lambda r: r["date"])

    running = Decimal(0)
    total_debit = Decimal(0)
    total_credit = Decimal(0)
    for row in rows:
        d = Decimal(row["debit"])
        c = Decimal(row["credit"])
        running += c - d
        total_debit += d
        total_credit += c
        row["balance"] = str(running)

    party_code = None
    party_name = None
    for bill in bills:
        if bill.supplierCode or bill.supplierName:
            party_code = bill.supplierCode
            party_name = bill.supplierName
            break
    if party_name is None:
        for pay in payments:
            if pay.supplierCode or pay.supplierName:
                party_code = pay.supplierCode
                party_name = pay.supplierName
                break

    return {
        "party": {"id": supplier_id, "name": party_name, "code": party_code},
        "lines": rows,
        "totals": {
            "debit": str(total_debit),
            "credit": str(total_credit),
            "balance": str(running),
        },
    }


def as_of_date_is_current(as_of: datetime) -> bool:
    """True when as-of is within the last minute (MV fast path eligible)."""

    now = datetime.now(timezone.utc)
    delta = abs((now - as_of).total_seconds())
    return delta < 60
