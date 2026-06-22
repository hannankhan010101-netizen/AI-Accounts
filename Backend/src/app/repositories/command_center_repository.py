"""Command center dashboard — single aggregated payload for business command center."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.dashboard_overview_repository import DashboardOverviewRepository
from app.repositories.inventory_repository import ProductBatchRepository
from app.repositories.journal_repository import JournalRepository
from app.repositories.smart_settings_repository import SmartSettingsRepository
from app.repositories.sql import command_center_queries as ccq
from app.repositories.sql import dashboard_overview_queries as doq
from app.repositories.sql.report_aggregate_queries import BANK_CASH_FLOW_MONTHLY_SQL
from app.services.activity_service import ActivityService
from app.services.aging_service import AgingService
from app.services.batch_expiry_alert_service import BatchExpiryAlertService
from app.services.dashboard_insights_service import build_insights
from app.services.smart_settings_runtime import SmartSettingsRuntime
from app.utils.period_range import resolve_period
from prisma_generated import Prisma

logger = logging.getLogger(__name__)


def _dec(value: Any) -> Decimal:
    if value is None:
        return Decimal(0)
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _change_pct(current: Decimal, prior: Decimal) -> float | None:
    if prior == 0:
        return None
    return float((current - prior) / abs(prior) * 100)


def _kpi_status_positive(current: Decimal, prior: Decimal, *, invert: bool = False) -> str:
    if current < 0:
        return "critical"
    change = _change_pct(current, prior)
    if change is None:
        return "neutral"
    good = change >= 0 if not invert else change <= 0
    if good:
        return "good"
    if change < -10:
        return "warn"
    return "neutral"


def _trend_from_rows(rows: list[Any], key: str = "total_sales", limit: int = 6) -> list[float]:
    return [float(_dec(r.get(key))) for r in rows[-limit:]]


def _build_executive_kpis(
    *,
    bank_total: Decimal,
    prior_bank: Decimal,
    revenue: Decimal,
    prior_revenue: Decimal,
    gross_profit: Decimal,
    prior_gross: Decimal,
    net_profit: Decimal,
    prior_net: Decimal,
    ar_outstanding: Decimal,
    prior_ar: Decimal,
    ap_outstanding: Decimal,
    prior_ap: Decimal,
    inventory_value: Decimal,
    prior_inv: Decimal,
    sales_trend: list[float],
    bank_trend: list[float],
    has_negative_bank: bool,
    expiring_alertable: int = 0,
    expiring_window_days: int = 30,
) -> list[dict[str, Any]]:
    cash_status = "critical" if has_negative_bank else _kpi_status_positive(bank_total, prior_bank)
    kpis: list[dict[str, Any]] = [
        {
            "id": "kpi-cash",
            "label": "Cash Available",
            "value": str(bank_total),
            "priorValue": str(prior_bank),
            "changePct": _change_pct(bank_total, prior_bank),
            "trendSeries": bank_trend,
            "status": cash_status,
            "drillDownHref": "/bank/balances",
        },
        {
            "id": "kpi-bank",
            "label": "Bank Balance",
            "value": str(bank_total),
            "priorValue": str(prior_bank),
            "changePct": _change_pct(bank_total, prior_bank),
            "trendSeries": bank_trend,
            "status": cash_status,
            "drillDownHref": "/bank/balances",
        },
        {
            "id": "kpi-revenue",
            "label": "Monthly Revenue",
            "value": str(revenue),
            "priorValue": str(prior_revenue),
            "changePct": _change_pct(revenue, prior_revenue),
            "trendSeries": sales_trend,
            "status": _kpi_status_positive(revenue, prior_revenue),
            "drillDownHref": "/reports/sale-summary-by-date",
        },
        {
            "id": "kpi-gross-profit",
            "label": "Gross Profit",
            "value": str(gross_profit),
            "priorValue": str(prior_gross),
            "changePct": _change_pct(gross_profit, prior_gross),
            "trendSeries": sales_trend,
            "status": "critical" if gross_profit < 0 else _kpi_status_positive(gross_profit, prior_gross),
            "drillDownHref": "/reports/profit-and-loss",
        },
        {
            "id": "kpi-net-profit",
            "label": "Net Profit",
            "value": str(net_profit),
            "priorValue": str(prior_net),
            "changePct": _change_pct(net_profit, prior_net),
            "trendSeries": sales_trend,
            "status": "critical" if net_profit < 0 else _kpi_status_positive(net_profit, prior_net),
            "drillDownHref": "/reports/profit-and-loss",
        },
        {
            "id": "kpi-ar",
            "label": "Accounts Receivable",
            "value": str(ar_outstanding),
            "priorValue": str(prior_ar),
            "changePct": _change_pct(ar_outstanding, prior_ar),
            "trendSeries": [float(ar_outstanding)] * max(1, len(sales_trend)),
            "status": _kpi_status_positive(ar_outstanding, prior_ar, invert=True),
            "drillDownHref": "/reports/ar-aging",
        },
        {
            "id": "kpi-ap",
            "label": "Accounts Payable",
            "value": str(ap_outstanding),
            "priorValue": str(prior_ap),
            "changePct": _change_pct(ap_outstanding, prior_ap),
            "trendSeries": [float(ap_outstanding)] * max(1, len(sales_trend)),
            "status": "neutral",
            "drillDownHref": "/reports/ap-aging",
        },
        {
            "id": "kpi-inventory-value",
            "label": "Inventory Value",
            "value": str(inventory_value),
            "priorValue": str(prior_inv),
            "changePct": _change_pct(inventory_value, prior_inv),
            "trendSeries": [float(inventory_value)] * max(1, len(sales_trend)),
            "status": "neutral",
            "drillDownHref": "/reports/stock-valuation",
        },
    ]
    if expiring_alertable > 0:
        kpis.append(
            {
                "id": "kpi-expiring-batches",
                "label": "Expiring batches",
                "value": str(expiring_alertable),
                "priorValue": "0",
                "changePct": None,
                "trendSeries": [float(expiring_alertable)],
                "status": "warn",
                "drillDownHref": "/inventory/batches?filter=expiring",
            }
        )
    return kpis


def _pct_breakdown(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    total = sum(_dec(r.get("amount")) for r in rows)
    if total <= 0:
        return []
    return [
        {
            "label": r["label"],
            "amount": str(_dec(r.get("amount"))),
            "pct": float(_dec(r.get("amount")) / total * 100),
        }
        for r in rows
    ]


def _overdue_from_aging(aging: dict[str, Any]) -> tuple[int, Decimal]:
    count = 0
    amount = Decimal(0)
    for row in aging.get("rows") or []:
        if row.get("bucket") == "Older":
            count += int(row.get("openInvoiceCount") or 0) or 1
            amount += _dec(row.get("balance"))
    for bucket in aging.get("buckets") or []:
        if bucket.get("label") == "Older":
            count = max(count, int(bucket.get("count") or 0))
            if _dec(bucket.get("total")) > amount:
                amount = _dec(bucket.get("total"))
    return count, amount


def _monthly_bank_balances(
    bank_balances: list[dict[str, Any]],
    bank_cash_flow: list[dict[str, Any]],
    *,
    now: datetime,
    months: int = 12,
) -> list[dict[str, str]]:
    month_specs: list[tuple[int, int]] = []
    year, month = now.year, now.month
    for _ in range(months):
        month_specs.append((year, month))
        month -= 1
        if month < 1:
            month = 12
            year -= 1
    month_specs.reverse()

    net_by_month = {
        str(row.get("month")): _dec(row.get("net"))
        for row in bank_cash_flow
        if row.get("month")
    }
    current_total = sum(_dec(r.get("balance")) for r in bank_balances)
    rolling = current_total
    out: list[dict[str, str]] = []
    for y, m in reversed(month_specs):
        key = f"{y:04d}-{m:02d}"
        out.insert(0, {"month": key, "balance": str(rolling)})
        rolling -= net_by_month.get(key, Decimal(0))
    return out


def _balance_at_month(monthly: list[dict[str, str]], dt: datetime) -> Decimal:
    key = dt.strftime("%Y-%m")
    for row in monthly:
        if row.get("month") == key:
            return _dec(row.get("balance"))
    return Decimal(0)


def _profit_from_classified(
    classified: list[dict[str, Any]], cogs: Decimal
) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    income_rows = [r for r in classified if r.get("categoryType") == "Income"]
    expense_rows = [r for r in classified if r.get("categoryType") == "Expense"]
    income_total = sum((_dec(r["credit"]) - _dec(r["debit"]) for r in income_rows), Decimal(0))
    expense_total = sum((_dec(r["debit"]) - _dec(r["credit"]) for r in expense_rows), Decimal(0))
    gross_profit = income_total - cogs if cogs > 0 else income_total - expense_total
    net_profit = income_total - expense_total
    return income_total, expense_total, gross_profit, net_profit


class CommandCenterRepository:
    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client
        self._overview = DashboardOverviewRepository(prisma_client)
        self._journals = JournalRepository(prisma_client)
        self._aging = AgingService(prisma_client)
        self._activity = ActivityService(prisma_client)
        self._audit = AuditLogRepository(prisma_client)
        self._batches = ProductBatchRepository(prisma_client)
        self._smart = SmartSettingsRepository(prisma_client)

    async def command_center(
        self,
        *,
        company_id: str,
        period: str = "fy",
        sales_granularity: str = "month",
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        date_from, date_to, prior_from, prior_to = resolve_period(period, now=now)
        twelve_months_ago = (now.replace(day=1) - timedelta(days=335)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        low_threshold = Decimal(10)
        overstock_threshold = Decimal(100)

        sales_sql = {
            "day": ccq.SALES_BY_DAY_SQL,
            "week": ccq.SALES_BY_WEEK_SQL,
        }.get(sales_granularity, ccq.SALES_BY_MONTH_PERIOD_SQL)

        (
            sales_rows,
            stock_rows,
            classified,
            bank_balances_raw,
            bank_cash_flow_raw,
            ar,
            ap,
            revenue_row,
            prior_revenue_row,
            inventory_value_row,
            low_stock_rows,
            oos_rows,
            overstock_rows,
            fast_movers,
            slow_movers,
            cogs_row,
            revenue_by_cat,
            sales_trend_rows,
            prior_classified,
            prior_cogs_row,
            prior_ar,
            prior_ap,
        ) = await asyncio.gather(
            self._db.query_raw(doq.SALES_BY_MONTH_SQL, company_id, date_from, date_to),
            self._db.query_raw(doq.STOCK_COUNTS_SQL, company_id, low_threshold),
            self._journals.classified_balances(
                company_id=company_id, date_from=date_from, date_to=date_to
            ),
            self._overview._fetch_bank_balances(company_id=company_id),
            self._db.query_raw(BANK_CASH_FLOW_MONTHLY_SQL, company_id, twelve_months_ago, now),
            self._aging.ar_aging(company_id=company_id, as_of_date=now),
            self._aging.ap_aging(company_id=company_id, as_of_date=now),
            self._db.query_raw(ccq.MONTHLY_REVENUE_SQL, company_id, date_from, date_to),
            self._db.query_raw(ccq.MONTHLY_REVENUE_SQL, company_id, prior_from, prior_to),
            self._db.query_raw(ccq.INVENTORY_VALUE_SQL, company_id),
            self._db.query_raw(ccq.INVENTORY_STOCK_ROWS_SQL, company_id, low_threshold),
            self._db.query_raw(ccq.INVENTORY_OUT_OF_STOCK_SQL, company_id),
            self._db.query_raw(ccq.INVENTORY_OVERSTOCK_SQL, company_id, overstock_threshold),
            self._db.query_raw(ccq.FAST_MOVERS_SQL, company_id, date_from, date_to),
            self._db.query_raw(ccq.SLOW_MOVERS_SQL, company_id, date_from, date_to),
            self._db.query_raw(ccq.COGS_TOTAL_SQL, company_id, date_from, date_to),
            self._db.query_raw(ccq.REVENUE_BY_CATEGORY_SQL, company_id, date_from, date_to),
            self._db.query_raw(sales_sql, company_id, date_from, date_to),
            self._journals.classified_balances(
                company_id=company_id, date_from=prior_from, date_to=prior_to
            ),
            self._db.query_raw(ccq.COGS_TOTAL_SQL, company_id, prior_from, prior_to),
            self._aging.ar_aging(company_id=company_id, as_of_date=prior_to),
            self._aging.ap_aging(company_id=company_id, as_of_date=prior_to),
        )

        activity_tasks = await asyncio.gather(
            self._activity.list_sales_activity(company_id=company_id, date_from=date_from.date().isoformat(), date_to=date_to.date().isoformat()),
            self._activity.list_purchases_activity(company_id=company_id, date_from=date_from.date().isoformat(), date_to=date_to.date().isoformat()),
            self._db.stockadjustment.find_many(
                where={"companyId": company_id},
                order={"adjustmentDate": "desc"},
                take=15,
            ),
            AuditLogRepository(self._db).list_filtered(
                company_id=company_id,
                user_id=None,
                date_from=None,
                date_to=None,
                take=15,
            ),
            return_exceptions=True,
        )

        sales_activity = activity_tasks[0] if isinstance(activity_tasks[0], list) else []
        purchase_activity = activity_tasks[1] if isinstance(activity_tasks[1], list) else []
        stock_adj_raw = activity_tasks[2] if isinstance(activity_tasks[2], list) else []
        audit_raw = activity_tasks[3] if isinstance(activity_tasks[3], list) else []

        income_rows = [r for r in classified if r["categoryType"] == "Income"]
        expense_rows = [r for r in classified if r["categoryType"] == "Expense"]
        income_total = sum((_dec(r["credit"]) - _dec(r["debit"]) for r in income_rows), Decimal(0))
        expense_total = sum((_dec(r["debit"]) - _dec(r["credit"]) for r in expense_rows), Decimal(0))
        cogs = _dec(cogs_row[0]["cogs"] if cogs_row else 0)
        prior_cogs = _dec(prior_cogs_row[0]["cogs"] if prior_cogs_row else 0)
        gross_profit = income_total - cogs if cogs > 0 else income_total - expense_total
        net_profit = income_total - expense_total
        _, _, prior_gross, prior_net = _profit_from_classified(prior_classified, prior_cogs)

        expense_breakdown = sorted(
            [
                {
                    "label": r["categoryName"] or r["name"] or r["nominalCode"],
                    "amount": _dec(r["debit"]) - _dec(r["credit"]),
                }
                for r in expense_rows
                if (_dec(r["debit"]) - _dec(r["credit"])) != 0
            ],
            key=lambda x: x["amount"],
            reverse=True,
        )[:8]
        expense_breakdown_dicts = [{"label": r["label"], "amount": str(r["amount"])} for r in expense_breakdown]

        revenue_breakdown = [
            {"label": r["label"], "amount": str(_dec(r.get("amount")))} for r in revenue_by_cat
        ]

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
                "balance": str(_dec(r.get("balance"))),
            }
            for r in bank_balances_raw
        ]
        bank_total = sum(_dec(r["balance"]) for r in bank_balances)
        has_negative_bank = any(_dec(r["balance"]) < 0 for r in bank_balances)

        bank_cash_flow = [
            {
                "month": r["month"],
                "inflow": str(_dec(r.get("inflow"))),
                "outflow": str(_dec(r.get("outflow"))),
                "net": str(_dec(r.get("inflow")) - _dec(r.get("outflow"))),
            }
            for r in bank_cash_flow_raw
        ]

        revenue = _dec(revenue_row[0]["total"] if revenue_row else 0)
        prior_revenue = _dec(prior_revenue_row[0]["total"] if prior_revenue_row else 0)
        inventory_value = _dec(inventory_value_row[0]["total_value"] if inventory_value_row else 0)

        ar_outstanding = _dec((ar.get("totals") or {}).get("outstanding"))
        ap_outstanding = _dec((ap.get("totals") or {}).get("outstanding"))
        prior_ar_outstanding = _dec((prior_ar.get("totals") or {}).get("outstanding"))
        prior_ap_outstanding = _dec((prior_ap.get("totals") or {}).get("outstanding"))
        ar_count, ar_amount = _overdue_from_aging(ar)
        ap_count, ap_amount = _overdue_from_aging(ap)

        monthly_bank = _monthly_bank_balances(bank_balances, bank_cash_flow, now=now)
        prior_bank = _balance_at_month(monthly_bank, prior_to)

        sales_trend = _trend_from_rows(sales_rows)
        bank_trend = [float(_dec(r.get("net"))) for r in bank_cash_flow[-6:]]

        turnover: float | None = None
        if inventory_value > 0 and cogs > 0:
            turnover = float(cogs / inventory_value)

        def _stock_row(r: Any) -> dict[str, Any]:
            return {
                "productCode": r.get("productCode"),
                "productName": r.get("productName"),
                "quantity": str(_dec(r.get("quantity"))),
                "value": str(_dec(r.get("value"))),
            }

        def _mover_row(r: Any) -> dict[str, Any]:
            return {
                "productCode": r.get("productCode"),
                "productName": r.get("productName"),
                "quantitySold": str(_dec(r.get("quantitySold"))),
                "revenue": str(_dec(r.get("revenue"))),
            }

        invoices = [r for r in sales_activity if r.get("entityType") == "invoice"][:10]
        payments = [r for r in purchase_activity if r.get("entityType") == "payment"][:10]
        recent = sorted(
            [*sales_activity[:10], *purchase_activity[:10]],
            key=lambda r: str(r.get("documentDate") or ""),
            reverse=True,
        )[:20]

        stock_adjustments = [
            {
                "entityType": "stock_adjustment",
                "entityId": str(r.id),
                "docType": "Stock Adjustment",
                "documentNumber": r.voucherNumber or str(r.id)[:8],
                "documentDate": r.adjustmentDate.isoformat() if r.adjustmentDate else "",
                "totalAmount": "0",
                "status": r.status or "posted",
            }
            for r in stock_adj_raw
        ]

        audit_entries = [
            {
                "id": str(r.id),
                "timestamp": r.createdAt.isoformat() if r.createdAt else "",
                "transactionType": r.transactionType,
                "transactionId": r.transactionId,
                "status": r.status,
                "details": r.details,
                "userId": r.userId,
                "userName": getattr(r, "userName", None),
            }
            for r in audit_raw
        ]

        gross_pct = float(gross_profit / income_total * 100) if income_total > 0 else 0.0
        net_pct = float(net_profit / income_total * 100) if income_total > 0 else 0.0

        smart_runtime = SmartSettingsRuntime(
            smart_settings_repository=self._smart,
            prisma=self._db,
        )
        alert_config = await smart_runtime.inventory_alerts_config(company_id=company_id)
        if alert_config.get("enabled", True):
            expiring_rows = await self._batches.list_expiring_batches(
                company_id=company_id,
                within_days=int(alert_config["windowDays"]),
                now=now,
            )
            expiry_svc = BatchExpiryAlertService(window_days=int(alert_config["windowDays"]))
            expiring_summary = expiry_svc.summarize_rows(expiring_rows, now=now)
        else:
            expiring_summary = {
                "windowDays": int(alert_config["windowDays"]),
                "expired": 0,
                "expiringSoon": 0,
                "totalAlertable": 0,
                "preview": [],
            }
        if expiring_summary["totalAlertable"] > 0:
            logger.info(
                "expiry_insights_emitted company=%s expired=%s expiring_soon=%s",
                company_id,
                expiring_summary["expired"],
                expiring_summary["expiringSoon"],
            )

        payload: dict[str, Any] = {
            "period": {
                "from": date_from.date().isoformat(),
                "to": date_to.date().isoformat(),
                "priorFrom": prior_from.date().isoformat(),
                "priorTo": prior_to.date().isoformat(),
                "key": period,
            },
            "executiveKpis": _build_executive_kpis(
                bank_total=bank_total,
                prior_bank=prior_bank,
                revenue=revenue,
                prior_revenue=prior_revenue,
                gross_profit=gross_profit,
                prior_gross=prior_gross,
                net_profit=net_profit,
                prior_net=prior_net,
                ar_outstanding=ar_outstanding,
                prior_ar=prior_ar_outstanding,
                ap_outstanding=ap_outstanding,
                prior_ap=prior_ap_outstanding,
                inventory_value=inventory_value,
                prior_inv=inventory_value,
                sales_trend=sales_trend,
                bank_trend=bank_trend,
                has_negative_bank=has_negative_bank,
                expiring_alertable=int(expiring_summary["totalAlertable"]),
                expiring_window_days=int(expiring_summary["windowDays"]),
            ),
            "bankCashFlow": bank_cash_flow,
            "bankBalances": bank_balances,
            "salesTrend": {
                "granularity": sales_granularity,
                "points": [
                    {"label": str(r.get("label")), "value": str(_dec(r.get("total_sales")))}
                    for r in sales_trend_rows
                ],
            },
            "salesByMonth": [
                {"month": str(r.get("month")), "totalSales": str(_dec(r.get("total_sales")))}
                for r in sales_rows
            ],
            "arAging": ar,
            "apAging": ap,
            "overdue": {
                "arCount": ar_count,
                "arAmount": str(ar_amount),
                "apCount": ap_count,
                "apAmount": str(ap_amount),
            },
            "topCustomers": [r for r in ar.get("rows") or [] if _dec(r.get("balance")) > 0][:10],
            "topSuppliers": [r for r in ap.get("rows") or [] if _dec(r.get("balance")) > 0][:10],
            "arTopParties": [r for r in ar.get("rows") or [] if _dec(r.get("balance")) > 0][:10],
            "apTopParties": [r for r in ap.get("rows") or [] if _dec(r.get("balance")) > 0][:10],
            "inventoryCommand": {
                "totalValue": str(inventory_value),
                "turnoverRatio": turnover,
                "lowStock": [_stock_row(r) for r in low_stock_rows],
                "outOfStock": [_stock_row(r) for r in oos_rows],
                "overstock": [_stock_row(r) for r in overstock_rows],
                "fastMovers": [_mover_row(r) for r in fast_movers],
                "slowMovers": [_mover_row(r) for r in slow_movers],
                "bucketCounts": stock_counts,
                "expiringBatches": expiring_summary,
            },
            "inventoryStock": stock_counts,
            "profitability": {
                "totals": {
                    "income": str(income_total),
                    "cogs": str(cogs),
                    "grossProfit": str(gross_profit),
                    "expense": str(expense_total),
                    "netProfit": str(net_profit),
                },
                "expenseBreakdown": _pct_breakdown(expense_breakdown_dicts),
                "revenueBreakdown": _pct_breakdown(revenue_breakdown),
                "margins": {"grossPct": gross_pct, "netPct": net_pct},
            },
            "profitAndLoss": {
                "totals": {
                    "income": str(income_total),
                    "expense": str(expense_total),
                    "netProfit": str(net_profit),
                },
                "expenseBreakdown": expense_breakdown_dicts,
            },
            "operationalActivity": {
                "recentTransactions": recent,
                "latestInvoices": invoices,
                "latestPayments": payments,
                "stockAdjustments": stock_adjustments,
                "auditEntries": audit_entries,
            },
            "financialYearFrom": date_from.date().isoformat(),
            "financialYearTo": date_to.date().isoformat(),
        }
        payload["insights"] = build_insights(payload)
        return payload
