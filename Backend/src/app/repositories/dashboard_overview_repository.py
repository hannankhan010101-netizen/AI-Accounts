"""Dashboard overview bundle — parallel SQL reads (Step 1)."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

from app.repositories.journal_repository import JournalRepository
from app.repositories.sql import dashboard_overview_queries as doq
from app.repositories.sql.report_aggregate_queries import BANK_CASH_FLOW_MONTHLY_SQL
from app.services.aging_service import AgingService
from prisma_generated import Prisma


def _as_decimal(value: Any) -> Decimal:
    if value is None:
        return Decimal(0)
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _build_overview_payload(
    *,
    company_id: str,
    now: datetime,
    fy_start: datetime,
    sales_rows: list[Any],
    stock_rows: list[Any],
    classified: list[dict],
    bank_balances_raw: list[Any],
    bank_cash_flow_raw: list[Any],
    ar: dict[str, Any],
    ap: dict[str, Any],
) -> dict[str, Any]:
    _ = company_id
    income_rows = [r for r in classified if r["categoryType"] == "Income"]
    expense_rows = [r for r in classified if r["categoryType"] == "Expense"]
    income_total = sum(
        (_as_decimal(r["credit"]) - _as_decimal(r["debit"]) for r in income_rows),
        Decimal(0),
    )
    expense_total = sum(
        (_as_decimal(r["debit"]) - _as_decimal(r["credit"]) for r in expense_rows),
        Decimal(0),
    )
    expense_breakdown = sorted(
        [
            {
                "label": r["categoryName"] or r["name"] or r["nominalCode"],
                "amount": str(_as_decimal(r["debit"]) - _as_decimal(r["credit"])),
            }
            for r in expense_rows
            if (_as_decimal(r["debit"]) - _as_decimal(r["credit"])) != 0
        ],
        key=lambda x: Decimal(x["amount"]),
        reverse=True,
    )[:8]

    sales_by_month = {
        str(row["month"]): _as_decimal(row.get("total_sales"))
        for row in sales_rows
        if row.get("month")
    }

    stock_counts = {"inStock": 0, "lowStock": 0, "outOfStock": 0, "oversold": 0}
    for row in stock_rows:
        bucket = row.get("bucket")
        if bucket in stock_counts:
            stock_counts[bucket] = int(row.get("cnt") or 0)

    bank_balances = [
        {
            "bankAccountId": r.get("bankAccountId"),
            "name": r.get("name"),
            "nominalCode": r.get("nominalCode"),
            "currency": r.get("currency"),
            "balance": str(_as_decimal(r.get("balance"))),
        }
        for r in bank_balances_raw
    ]

    bank_cash_flow = [
        {
            "month": r["month"],
            "inflow": str(_as_decimal(r.get("inflow"))),
            "outflow": str(_as_decimal(r.get("outflow"))),
            "net": str(
                _as_decimal(r.get("inflow")) - _as_decimal(r.get("outflow"))
            ),
        }
        for r in bank_cash_flow_raw
    ]

    ar_top = [r for r in ar["rows"] if Decimal(r["balance"]) > 0][:10]
    ap_top = [r for r in ap["rows"] if Decimal(r["balance"]) > 0][:10]

    month_specs: list[tuple[int, int]] = []
    year, month = now.year, now.month
    for _ in range(12):
        month_specs.append((year, month))
        month -= 1
        if month < 1:
            month = 12
            year -= 1
    month_specs.reverse()

    net_by_month = {
        str(row.get("month")): Decimal(str(row.get("net", 0)))
        for row in bank_cash_flow
        if row.get("month")
    }
    current_bank_total = sum(Decimal(r["balance"]) for r in bank_balances)
    monthly_bank_balance: list[dict[str, str]] = []
    rolling = current_bank_total
    for y, m in reversed(month_specs):
        key = f"{y:04d}-{m:02d}"
        monthly_bank_balance.insert(0, {"month": key, "balance": str(rolling)})
        rolling -= net_by_month.get(key, Decimal(0))

    return {
        "financialYearFrom": fy_start.date().isoformat(),
        "financialYearTo": now.date().isoformat(),
        "bankBalances": bank_balances,
        "bankCashFlow": bank_cash_flow,
        "monthlyBankBalance": monthly_bank_balance,
        "profitAndLoss": {
            "totals": {
                "income": str(income_total),
                "expense": str(expense_total),
                "netProfit": str(income_total - expense_total),
            },
            "expenseBreakdown": expense_breakdown,
        },
        "salesByMonth": [
            {"month": m, "totalSales": str(t)}
            for m, t in sorted(sales_by_month.items())
        ],
        "inventoryStock": stock_counts,
        "arAging": ar,
        "apAging": ap,
        "arTopParties": ar_top,
        "apTopParties": ap_top,
    }


class DashboardOverviewRepository:
    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client
        self._journals = JournalRepository(prisma_client)
        self._aging = AgingService(prisma_client)

    async def overview(self, *, company_id: str) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        fy_start = datetime(now.year, 1, 1, tzinfo=timezone.utc)
        twelve_months_ago = (now.replace(day=1) - timedelta(days=335)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        low_threshold = Decimal(10)

        (
            sales_rows,
            stock_rows,
            classified,
            bank_balances_raw,
            bank_cash_flow_raw,
            ar,
            ap,
        ) = await asyncio.gather(
            self._db.query_raw(
                doq.SALES_BY_MONTH_SQL, company_id, fy_start, now
            ),
            self._db.query_raw(
                doq.STOCK_COUNTS_SQL, company_id, low_threshold
            ),
            self._journals.classified_balances(
                company_id=company_id, date_from=fy_start, date_to=now
            ),
            self._fetch_bank_balances(company_id=company_id),
            self._db.query_raw(
                BANK_CASH_FLOW_MONTHLY_SQL, company_id, twelve_months_ago, now
            ),
            self._aging.ar_aging(company_id=company_id, as_of_date=now),
            self._aging.ap_aging(company_id=company_id, as_of_date=now),
        )

        return await asyncio.to_thread(
            _build_overview_payload,
            company_id=company_id,
            now=now,
            fy_start=fy_start,
            sales_rows=sales_rows,
            stock_rows=stock_rows,
            classified=classified,
            bank_balances_raw=bank_balances_raw,
            bank_cash_flow_raw=bank_cash_flow_raw,
            ar=ar,
            ap=ap,
        )

    async def _fetch_bank_balances(self, *, company_id: str) -> list[dict[str, Any]]:
        try:
            return await self._db.query_raw(
                doq.BANK_ACCOUNT_BALANCES_SQL, company_id
            )
        except Exception:  # noqa: BLE001
            from app.services.report_query_service import ReportQueryService

            rows = await ReportQueryService(prisma=self._db).execute(
                company_id=company_id,
                report_id="BANK_BAL",
                criteria={"skipCache": True},
            )
            return [
                {
                    "bankAccountId": r.get("bankAccountId"),
                    "name": r.get("name"),
                    "nominalCode": r.get("nominalCode"),
                    "currency": r.get("currency"),
                    "balance": r.get("balance"),
                }
                for r in rows
            ]
