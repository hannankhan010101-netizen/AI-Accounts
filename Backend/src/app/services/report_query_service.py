"""SQL-backed report execution for catalog report IDs — P2."""

from __future__ import annotations

import asyncio
from calendar import monthrange
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from prisma_generated import Prisma

from app.core.async_io import maybe_thread
from app.constants.report_aliases import resolve_report_handler_id
from app.core.report_cache import get_report_cache
from app.repositories.journal_repository import JournalRepository
from app.repositories.sql.report_aggregate_queries import (
    ADVANCED_STOCK_BY_PRODUCT_SQL,
    ASSEMBLY_COMPONENT_DETAIL_SQL,
    ASSEMBLY_JOB_LINE_COSTS_SQL,
    ASSEMBLY_TEMPLATE_SUMMARY_SQL,
    BANK_CASH_FLOW_MONTHLY_SQL,
    BUDGET_ACTUAL_BY_NOMINAL_SQL,
    CUSTOMER_PERFORMANCE_SQL,
    CUSTOMER_SALES_ACTIVITY_SQL,
    PRODUCT_PURCHASES_BY_PRODUCT_SQL,
    PRODUCT_SALES_BY_PRODUCT_SQL,
    PROJECT_PAYMENTS_BY_CODE_SQL,
    PURCHASE_SUMMARY_BY_SUPPLIER_SQL,
    SALE_SUMMARY_BY_CUSTOMER_SQL,
    SALE_SUMMARY_BY_CUSTOM_FIELD_SQL,
    SALE_SUMMARY_BY_DATE_SQL,
    STOCK_BATCH_QUANTITY_SQL,
    STOCK_MOVEMENT_LINES_SQL,
    STOCK_TRANSFER_LINES_SQL,
    STOCK_VALUATION_SQL,
)
from app.services.aging_service import AgingService
from app.services.grni_service import GrniService
from app.utils.keyset_pagination import (
    apply_asc_code_keyset,
    apply_desc_date_keyset,
    attach_pagination_meta,
    page_size_from_criteria,
    parse_cursor_datetime,
    trim_keyset_page,
    trim_keyset_page_code,
)


def _merge_product_activity(
    sales_rows: list[dict],
    purchase_rows: list[dict],
    stock_rows: list[dict],
    products_list: list[Any],
) -> list[dict]:
    products = {p.code: p for p in products_list}
    sales_map = {
        str(r["productCode"]): Decimal(str(r.get("totalSales", 0))) for r in sales_rows
    }
    purchase_map = {
        str(r["productCode"]): Decimal(str(r.get("totalPurchases", 0)))
        for r in purchase_rows
    }
    qty_map: dict[str, Decimal] = {}
    for row in stock_rows:
        code = str(row.get("productCode") or "—")
        qty_map[code] = qty_map.get(code, Decimal(0)) + Decimal(
            str(row.get("quantityOnHand", 0))
        )
    codes = sorted(set(sales_map) | set(purchase_map) | set(qty_map))
    out: list[dict] = []
    for code in codes:
        prod = products.get(code)
        out.append(
            {
                "productCode": code,
                "productName": prod.name if prod else None,
                "quantityOnHand": str(qty_map.get(code, Decimal(0))),
                "totalSales": str(sales_map.get(code, Decimal(0))),
                "totalPurchases": str(purchase_map.get(code, Decimal(0))),
            }
        )
    return sorted(out, key=lambda r: Decimal(str(r["totalSales"])), reverse=True)


def _merge_product_performance(
    sales_rows: list[dict],
    purchase_rows: list[dict],
    products_list: list[Any],
) -> list[dict]:
    products = {p.code: p for p in products_list}
    sales_map = {
        str(r["productCode"]): Decimal(str(r.get("totalSales", 0))) for r in sales_rows
    }
    purchase_map = {
        str(r["productCode"]): Decimal(str(r.get("totalPurchases", 0)))
        for r in purchase_rows
    }
    codes = sorted(set(sales_map) | set(purchase_map))
    out: list[dict] = []
    for code in codes:
        sales = sales_map.get(code, Decimal(0))
        purchases = purchase_map.get(code, Decimal(0))
        prod = products.get(code)
        out.append(
            {
                "productCode": code,
                "productName": prod.name if prod else None,
                "totalSales": str(sales),
                "totalPurchases": str(purchases),
                "grossMargin": str(sales - purchases),
            }
        )
    return sorted(out, key=lambda r: Decimal(str(r["totalSales"])), reverse=True)


def _merge_customer_products(customer_id: str, lines: list[dict]) -> list[dict]:
    totals: dict[str, Decimal] = {}
    for line in lines:
        code = str(line.get("productCode") or "—")
        totals[code] = totals.get(code, Decimal(0)) + Decimal(
            str(line.get("lineTotal", 0))
        )
    return [
        {"customerId": customer_id, "productCode": code, "totalQtySales": str(amount)}
        for code, amount in sorted(totals.items(), key=lambda x: -x[1])
    ]


class ReportQueryService:
    def __init__(self, *, prisma: Prisma) -> None:
        self._db = prisma
        self._aging = AgingService(prisma)
        self._journals = JournalRepository(prisma)
        self._grni = GrniService(prisma=prisma)

    async def execute(
        self, *, company_id: str, report_id: str, criteria: dict[str, Any]
    ) -> list[dict[str, Any]]:
        handler_key = resolve_report_handler_id(report_id)
        handlers = {
            "028": self._sales_invoices_by_date,
            "029": self._sales_invoices_by_customer,
            "035": self._customer_list,
            "047": self._customer_balances,
            "048": self._purchase_bills_by_date,
            "067": self._supplier_balances,
            "071": self._bank_payments,
            "078": self._products_list,
            "STOCK_XFR": self._stock_transfer_detail,
            "PROD_ACT": self._product_activity_summary,
            "148": self._stock_valuation,
            "300": self._bank_payment_receipt_data,
            "032": self._sale_summary_by_date,
            "080": self._stock_quantity,
            "174": self._stock_movement,
            "GRNI": self._grni_report,
            "TB": self._trial_balance,
            "PNL": self._profit_and_loss,
            "BS": self._balance_sheet,
            "034": self._customer_statement,
            "085": self._product_sale_by_product,
            "087": self._product_purchase_by_product,
            "162": self._product_performance,
            "030": self._sales_invoice_line_detail,
            "031": self._sales_invoice_line_by_customer,
            "033": self._sale_summary_by_customer,
            "054": self._supplier_statement,
            "182": self._customer_performance,
            "GL": self._general_ledger,
            "079": self._price_list,
            "082": self._out_of_stock,
            "083": self._low_stock,
            "145": self._customer_products,
            "051": self._purchase_bills_by_supplier,
            "143": self._customer_outstanding_items,
            "175": self._advanced_stock_quantity,
            "181": self._multi_unit_price_list,
            "185": self._sale_summary_by_field,
            "311": self._customer_field_activity_summary,
            "BANK_BAL": self._bank_account_balances,
            "BANK_CF": self._bank_cash_flow_monthly,
            "ASM_JOB": self._assembly_job_cost_summary,
            "PRJ_PAY": self._project_payments_report,
            "FIN_MTB": self._financial_monthly_balances,
            "BANK_REC": self._bank_receipts_list,
            "BANK_XFR": self._bank_transfers_list,
            "BANK_ACT": self._bank_activity_summary,
            "ASM_TPL": self._assembly_templates_list,
            "FIN_CMP": self._financial_comparative_pnl,
            "FIN_PNL_CAT": self._financial_comparative_pnl_by_category,
            "ASM_WIP": self._assembly_wip_jobs,
            "ASM_COMP": self._assembly_component_cost_detail,
            "FIN_TB12": self._financial_trial_balance_by_month,
            "BUDGET_VS_ACTUAL": self._budget_vs_actual,
            "AR_AGING": self._ar_aging_report,
            "AP_AGING": self._ap_aging_report,
        }
        handler = handlers.get(handler_key)
        if handler is None:
            return [
                {
                    "reportId": report_id,
                    "resolvedHandler": handler_key,
                    "message": "Report query not implemented yet.",
                    "criteria": criteria,
                }
            ]
        cache = get_report_cache()
        if not criteria.get("skipCache"):
            cached = await cache.get_rows(
                company_id=company_id,
                report_id=report_id,
                criteria=criteria,
            )
            if cached is not None:
                return self._finalize_rows(cached, criteria)
        rows = await handler(company_id=company_id, criteria=criteria)
        if not criteria.get("skipCache"):
            await cache.set_rows(
                company_id=company_id,
                report_id=report_id,
                criteria=criteria,
                rows=rows,
            )
        return self._finalize_rows(rows, criteria)

    def _finalize_rows(self, rows: list[dict], criteria: dict[str, Any]) -> list[dict]:
        if criteria.get("cursorDate") or criteria.get("cursorCode"):
            return rows
        return self._paginate(rows, criteria)

    def _paginate(self, rows: list[dict], criteria: dict[str, Any]) -> list[dict]:
        page = max(1, int(criteria.get("page") or 1))
        page_size = min(max(1, int(criteria.get("pageSize") or 200)), 5000)
        start = (page - 1) * page_size
        sliced = rows[start : start + page_size]
        if criteria.get("includePaginationMeta"):
            return [
                {
                    "_meta": {
                        "page": page,
                        "pageSize": page_size,
                        "totalRows": len(rows),
                        "returnedRows": len(sliced),
                    }
                },
                *sliced,
            ]
        return sliced

    def _parse_dates(self, criteria: dict[str, Any]) -> tuple[datetime | None, datetime | None]:
        date_from = criteria.get("dateFrom")
        date_to = criteria.get("dateTo")
        df = datetime.fromisoformat(str(date_from).replace("Z", "+00:00")) if date_from else None
        dt = datetime.fromisoformat(str(date_to).replace("Z", "+00:00")) if date_to else None
        return df, dt

    def _criteria_status(self, criteria: dict[str, Any], *, default: str = "posted") -> str | None:
        raw = criteria.get("status")
        if raw is None or raw == "":
            return default or None
        normalized = str(raw).strip().lower()
        if normalized in {"all", "any", "*"}:
            return None
        return str(raw).strip()

    def _apply_document_filters(
        self,
        where: dict[str, Any],
        criteria: dict[str, Any],
        *,
        default_status: str = "posted",
    ) -> dict[str, Any]:
        status = self._criteria_status(criteria, default=default_status)
        if status:
            where["status"] = status
        if criteria.get("customerId"):
            where["customerId"] = str(criteria["customerId"])
        if criteria.get("supplierId"):
            where["supplierId"] = str(criteria["supplierId"])
        return where

    def _sql_invoice_filters(
        self, criteria: dict[str, Any]
    ) -> tuple[str | None, datetime | None, datetime | None]:
        return (
            self._criteria_status(criteria, default="posted"),
            *self._parse_dates(criteria),
        )

    def _sql_date_keyset_params(
        self, criteria: dict[str, Any]
    ) -> tuple[datetime | None, datetime | None, datetime | None, str | None]:
        df, dt = self._parse_dates(criteria)
        cursor_date = parse_cursor_datetime(criteria.get("cursorDate"))
        cursor_id = criteria.get("cursorId")
        return df, dt, cursor_date, str(cursor_id) if cursor_id else None

    async def _sales_invoices_by_date(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        df, dt = self._parse_dates(criteria)
        where = self._apply_document_filters({"companyId": company_id}, criteria)
        if df or dt:
            rng: dict = {}
            if df:
                rng["gte"] = df
            if dt:
                rng["lte"] = dt
            where["invoiceDate"] = rng
        where = apply_desc_date_keyset(where, criteria=criteria, date_field="invoiceDate")
        page_size = page_size_from_criteria(criteria)
        rows = await self._db.salesinvoice.find_many(
            where=where,
            order=[{"invoiceDate": "desc"}, {"id": "desc"}],
            take=page_size + 1,
        )

        def _row(r: Any) -> dict:
            return {
                "id": r.id,
                "invoiceNumber": r.invoiceNumber,
                "invoiceDate": r.invoiceDate.isoformat(),
                "customerId": r.customerId,
                "totalAmount": str(r.totalAmount),
            }

        out, next_cursor = trim_keyset_page(
            rows, page_size=page_size, to_dict=_row, date_field="invoiceDate"
        )
        return attach_pagination_meta(out, criteria=criteria, next_cursor=next_cursor)

    async def _sales_invoices_by_customer(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        where = self._apply_document_filters({"companyId": company_id}, criteria)
        where = apply_desc_date_keyset(where, criteria=criteria, date_field="invoiceDate")
        page_size = page_size_from_criteria(criteria)
        rows = await self._db.salesinvoice.find_many(
            where=where,
            order=[{"invoiceDate": "desc"}, {"id": "desc"}],
            take=page_size + 1,
        )

        def _row(r: Any) -> dict:
            return {
                "id": r.id,
                "customerId": r.customerId,
                "invoiceNumber": r.invoiceNumber,
                "invoiceDate": r.invoiceDate.isoformat(),
                "totalAmount": str(r.totalAmount),
            }

        out, next_cursor = trim_keyset_page(
            rows, page_size=page_size, to_dict=_row, date_field="invoiceDate"
        )
        return attach_pagination_meta(out, criteria=criteria, next_cursor=next_cursor)

    async def _customer_list(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        where = apply_asc_code_keyset(
            {"companyId": company_id}, criteria=criteria, code_field="code"
        )
        page_size = page_size_from_criteria(criteria)
        rows = await self._db.customer.find_many(
            where=where,
            order=[{"code": "asc"}, {"id": "asc"}],
            take=page_size + 1,
        )

        def _row(c: Any) -> dict:
            return {"code": c.code, "name": c.name, "id": c.id}

        out, next_cursor = trim_keyset_page_code(
            rows, page_size=page_size, to_dict=_row, code_field="code"
        )
        return attach_pagination_meta(out, criteria=criteria, next_cursor=next_cursor)

    async def _customer_balances(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        df, dt = self._parse_dates(criteria)
        as_of = dt or df
        aging = await self._aging.ar_aging(company_id=company_id, as_of_date=as_of)
        return aging.get("rows", [])

    async def _purchase_bills_by_date(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        df, dt = self._parse_dates(criteria)
        where = self._apply_document_filters({"companyId": company_id}, criteria)
        if df or dt:
            rng: dict = {}
            if df:
                rng["gte"] = df
            if dt:
                rng["lte"] = dt
            where["billDate"] = rng
        where = apply_desc_date_keyset(where, criteria=criteria, date_field="billDate")
        page_size = page_size_from_criteria(criteria)
        rows = await self._db.supplierbill.find_many(
            where=where,
            order=[{"billDate": "desc"}, {"id": "desc"}],
            take=page_size + 1,
        )

        def _row(r: Any) -> dict:
            return {
                "id": r.id,
                "billNumber": r.billNumber,
                "billDate": r.billDate.isoformat(),
                "supplierId": r.supplierId,
                "totalAmount": str(r.totalAmount),
            }

        out, next_cursor = trim_keyset_page(
            rows, page_size=page_size, to_dict=_row, date_field="billDate"
        )
        return attach_pagination_meta(out, criteria=criteria, next_cursor=next_cursor)

    async def _supplier_balances(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        df, dt = self._parse_dates(criteria)
        as_of = dt or df
        aging = await self._aging.ap_aging(company_id=company_id, as_of_date=as_of)
        return aging.get("rows", [])

    async def _bank_payments(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        df, dt = self._parse_dates(criteria)
        where: dict[str, Any] = {"companyId": company_id}
        if df or dt:
            rng: dict = {}
            if df:
                rng["gte"] = df
            if dt:
                rng["lte"] = dt
            where["paymentDate"] = rng
        where = apply_desc_date_keyset(where, criteria=criteria, date_field="paymentDate")
        page_size = page_size_from_criteria(criteria)
        rows = await self._db.bankpayment.find_many(
            where=where,
            order=[{"paymentDate": "desc"}, {"id": "desc"}],
            take=page_size + 1,
        )

        def _row(p: Any) -> dict:
            return {
                "id": p.id,
                "voucherNumber": p.voucherNumber,
                "paymentDate": p.paymentDate.isoformat(),
                "amount": str(p.totalAmount),
                "nominalCode": p.nominalCode,
                "direction": "out",
            }

        out, next_cursor = trim_keyset_page(
            rows, page_size=page_size, to_dict=_row, date_field="paymentDate"
        )
        return attach_pagination_meta(out, criteria=criteria, next_cursor=next_cursor)

    async def _products_list(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        where: dict[str, Any] = {"companyId": company_id, "isArchived": False}
        if criteria.get("productCode"):
            where["code"] = str(criteria["productCode"])
        where = apply_asc_code_keyset(where, criteria=criteria, code_field="code")
        page_size = page_size_from_criteria(criteria)
        rows = await self._db.product.find_many(
            where=where,
            order=[{"code": "asc"}, {"id": "asc"}],
            take=page_size + 1,
        )

        def _row(p: Any) -> dict:
            return {
                "code": p.code,
                "name": p.name,
                "cost": str(p.cost),
                "isStock": p.isStock,
            }

        out, next_cursor = trim_keyset_page_code(
            rows, page_size=page_size, to_dict=_row, code_field="code"
        )
        return attach_pagination_meta(out, criteria=criteria, next_cursor=next_cursor)

    async def _stock_valuation(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        batch_where: dict[str, Any] = {"companyId": company_id}
        if criteria.get("productCode"):
            batch_where["productCode"] = str(criteria["productCode"])
        product_filter = (
            str(criteria["productCode"]) if criteria.get("productCode") else None
        )
        raw = await self._db.query_raw(
            STOCK_VALUATION_SQL, company_id, product_filter
        )
        return [
            {
                "productCode": r["productCode"],
                "batchNumber": r["batchNumber"],
                "quantityOnHand": str(r["quantityOnHand"]),
                "unitCost": str(r["unitCost"]),
                "value": str(r["value"]),
            }
            for r in raw
        ]

    async def _bank_payment_receipt_data(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        df, dt = self._parse_dates(criteria)
        receipt_where: dict[str, Any] = {"companyId": company_id}
        if df or dt:
            rng: dict = {}
            if df:
                rng["gte"] = df
            if dt:
                rng["lte"] = dt
            receipt_where["receiptDate"] = rng
        receipt_where = apply_desc_date_keyset(
            receipt_where, criteria=criteria, date_field="receiptDate"
        )
        page_size = page_size_from_criteria(criteria)
        payments, receipts = await asyncio.gather(
            self._bank_payments(company_id=company_id, criteria=criteria),
            self._db.bankreceipt.find_many(
                where=receipt_where,
                order=[{"receiptDate": "desc"}, {"id": "desc"}],
                take=page_size + 1,
            ),
        )
        receipts = receipts[:page_size]
        for r in receipts:
            payments.append(
                {
                    "id": r.id,
                    "voucherNumber": r.voucherNumber,
                    "receiptDate": r.receiptDate.isoformat(),
                    "amount": str(r.totalAmount),
                    "direction": "in",
                }
            )
        return payments

    async def _sale_summary_by_date(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        df, dt = self._parse_dates(criteria)
        status = self._criteria_status(criteria, default="posted")
        customer_id = criteria.get("customerId")
        raw = await self._db.query_raw(
            SALE_SUMMARY_BY_DATE_SQL,
            company_id,
            status,
            df,
            dt,
            str(customer_id) if customer_id else None,
        )
        return [
            {
                "invoiceDate": (
                    r["invoiceDate"].isoformat()
                    if hasattr(r["invoiceDate"], "isoformat")
                    else str(r["invoiceDate"])
                ),
                "totalSales": str(r["totalSales"]),
            }
            for r in raw
        ]

    async def _stock_quantity(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        product_code = criteria.get("productCode")
        where: dict[str, Any] = {"companyId": company_id}
        if product_code:
            where["productCode"] = str(product_code)
        product_filter = str(product_code) if product_code else None
        raw = await self._db.query_raw(
            STOCK_BATCH_QUANTITY_SQL, company_id, product_filter
        )
        return [
            {
                "productCode": r["productCode"],
                "batchNumber": r["batchNumber"],
                "quantityOnHand": str(r["quantityOnHand"]),
            }
            for r in raw
        ]

    async def _stock_movement(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        df, dt, cursor_date, cursor_id = self._sql_date_keyset_params(criteria)
        product_code = criteria.get("productCode")
        page_size = page_size_from_criteria(criteria, maximum=2000)
        raw = await self._db.query_raw(
            STOCK_MOVEMENT_LINES_SQL,
            company_id,
            df,
            dt,
            str(product_code) if product_code else None,
            cursor_date,
            cursor_id,
            page_size + 1,
        )
        has_more = len(raw) > page_size
        if has_more:
            raw = raw[:page_size]
        out: list[dict] = []
        for row in raw:
            movement_date = row["movementDate"]
            out.append(
                {
                    "id": row["id"],
                    "voucherNumber": row["voucherNumber"],
                    "date": (
                        movement_date.isoformat()
                        if hasattr(movement_date, "isoformat")
                        else str(movement_date)
                    ),
                    "productCode": row["productCode"],
                    "quantityDelta": str(row["quantityDelta"]),
                    "kind": "adjustment",
                }
            )
        next_cursor = None
        if has_more and raw:
            last = raw[-1]
            last_date = last["movementDate"]
            next_cursor = {
                "cursorDate": (
                    last_date.isoformat()
                    if hasattr(last_date, "isoformat")
                    else str(last_date)
                ),
                "cursorId": last["id"],
                "hasMore": True,
            }
        return attach_pagination_meta(out, criteria=criteria, next_cursor=next_cursor)

    async def _stock_transfer_detail(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        df, dt, cursor_date, cursor_id = self._sql_date_keyset_params(criteria)
        product_code = criteria.get("productCode")
        page_size = page_size_from_criteria(criteria, maximum=2000)
        raw = await self._db.query_raw(
            STOCK_TRANSFER_LINES_SQL,
            company_id,
            df,
            dt,
            str(product_code) if product_code else None,
            cursor_date,
            cursor_id,
            page_size + 1,
        )
        has_more = len(raw) > page_size
        if has_more:
            raw = raw[:page_size]
        out: list[dict] = []
        for row in raw:
            transfer_date = row["transferDate"]
            out.append(
                {
                    "id": row["id"],
                    "voucherNumber": row["voucherNumber"],
                    "transferDate": (
                        transfer_date.isoformat()
                        if hasattr(transfer_date, "isoformat")
                        else str(transfer_date)
                    ),
                    "fromLocationCode": row["fromLocationCode"],
                    "toLocationCode": row["toLocationCode"],
                    "productCode": row["productCode"],
                    "quantity": str(row["quantity"]),
                    "unitCost": str(row["unitCost"]),
                    "lineValue": str(row["lineValue"]),
                }
            )
        next_cursor = None
        if has_more and raw:
            last = raw[-1]
            last_date = last["transferDate"]
            next_cursor = {
                "cursorDate": (
                    last_date.isoformat()
                    if hasattr(last_date, "isoformat")
                    else str(last_date)
                ),
                "cursorId": last["id"],
                "hasMore": True,
            }
        return attach_pagination_meta(out, criteria=criteria, next_cursor=next_cursor)

    async def _product_activity_summary(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        sales_rows, purchase_rows, stock_rows, products_list = await asyncio.gather(
            self._product_sale_by_product(company_id=company_id, criteria=criteria),
            self._product_purchase_by_product(company_id=company_id, criteria=criteria),
            self._stock_quantity(company_id=company_id, criteria=criteria),
            self._db.product.find_many(where={"companyId": company_id}),
        )
        return await maybe_thread(
            _merge_product_activity,
            sales_rows,
            purchase_rows,
            stock_rows,
            products_list,
            min_rows=200,
            row_count=max(len(sales_rows), len(purchase_rows)),
        )

    async def _grni_report(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        _ = criteria
        return await self._grni.report(company_id=company_id)

    async def _trial_balance(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        _, dt = self._parse_dates(criteria)
        return await self._journals.trial_balance(
            company_id=company_id, as_of_date=dt
        )

    async def _profit_and_loss(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        df, dt = self._parse_dates(criteria)
        rows = await self._journals.classified_balances(
            company_id=company_id, date_from=df, date_to=dt
        )
        return [r for r in rows if r.get("categoryType") in {"Income", "Expense"}]

    async def _balance_sheet(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        df, dt = self._parse_dates(criteria)
        rows = await self._journals.classified_balances(
            company_id=company_id, date_from=df, date_to=dt
        )
        return [
            r
            for r in rows
            if r.get("categoryType") in {"Asset", "Liability", "Equity"}
        ]

    async def _customer_statement(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        customer_id = criteria.get("customerId")
        if not customer_id:
            return [{"message": "customerId is required"}]
        df, dt = self._parse_dates(criteria)
        result = await self._aging.customer_statement(
            company_id=company_id,
            customer_id=str(customer_id),
            date_from=df,
            date_to=dt,
        )
        return result.get("lines", [])

    async def _supplier_statement(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        supplier_id = criteria.get("supplierId")
        if not supplier_id:
            return [{"message": "supplierId is required"}]
        df, dt = self._parse_dates(criteria)
        result = await self._aging.supplier_statement(
            company_id=company_id,
            supplier_id=str(supplier_id),
            date_from=df,
            date_to=dt,
        )
        return result.get("lines", [])

    async def _sale_summary_by_customer(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        status, df, dt = self._sql_invoice_filters(criteria)
        raw = await self._db.query_raw(
            SALE_SUMMARY_BY_CUSTOMER_SQL, company_id, status, df, dt
        )
        return [
            {"customerId": r["customerId"], "totalSales": str(r["totalSales"])}
            for r in raw
        ]

    async def _sales_invoice_line_by_customer(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        if not criteria.get("customerId"):
            return [{"message": "customerId is required"}]
        return await self._sales_invoice_line_detail(
            company_id=company_id, criteria=criteria
        )

    async def _customer_performance(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        status, df, dt = self._sql_invoice_filters(criteria)
        raw = await self._db.query_raw(
            CUSTOMER_PERFORMANCE_SQL, company_id, status, df, dt
        )
        return [
            {
                "customerId": r["customerId"],
                "customerCode": r.get("customerCode"),
                "customerName": r.get("customerName"),
                "totalSales": str(r["totalSales"]),
            }
            for r in raw
        ]

    async def _general_ledger(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        nominal_code = criteria.get("nominalCode")
        if not nominal_code:
            return [{"message": "nominalCode is required"}]
        df, dt = self._parse_dates(criteria)
        result = await self._journals.general_ledger(
            company_id=company_id,
            nominal_code=str(nominal_code),
            date_from=df,
            date_to=dt,
        )
        lines = result.get("lines", [])
        if isinstance(lines, list):
            return lines
        return []

    async def _sales_invoice_line_detail(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        df, dt = self._parse_dates(criteria)
        where = self._apply_document_filters({"companyId": company_id}, criteria)
        product_code = criteria.get("productCode")
        if df or dt:
            rng: dict = {}
            if df:
                rng["gte"] = df
            if dt:
                rng["lte"] = dt
            where["invoiceDate"] = rng
        where = apply_desc_date_keyset(where, criteria=criteria, date_field="invoiceDate")
        page_size = page_size_from_criteria(criteria, maximum=500)
        invoices = await self._db.salesinvoice.find_many(
            where=where,
            include={"lines": True},
            order=[{"invoiceDate": "desc"}, {"id": "desc"}],
            take=page_size + 1,
        )
        invoices = invoices[:page_size]
        out: list[dict] = []
        for inv in invoices:
            for line in inv.lines or []:
                if product_code and line.productCode != product_code:
                    continue
                out.append(
                    {
                        "invoiceId": inv.id,
                        "invoiceNumber": inv.invoiceNumber,
                        "invoiceDate": inv.invoiceDate.isoformat(),
                        "productCode": line.productCode,
                        "quantity": str(line.quantity),
                        "rate": str(line.rate),
                        "lineTotal": str(line.lineTotal),
                    }
                )
        return out

    async def _product_sale_by_product(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        status, df, dt = self._sql_invoice_filters(criteria)
        product_code = criteria.get("productCode")
        raw = await self._db.query_raw(
            PRODUCT_SALES_BY_PRODUCT_SQL,
            company_id,
            status,
            df,
            dt,
            str(product_code) if product_code else None,
        )
        return [
            {"productCode": r["productCode"], "totalSales": str(r["totalSales"])}
            for r in raw
        ]

    async def _product_purchase_by_product(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        status, df, dt = self._sql_invoice_filters(criteria)
        product_code = criteria.get("productCode")
        raw = await self._db.query_raw(
            PRODUCT_PURCHASES_BY_PRODUCT_SQL,
            company_id,
            status,
            df,
            dt,
            str(product_code) if product_code else None,
        )
        return [
            {
                "productCode": r["productCode"],
                "totalPurchases": str(r["totalPurchases"]),
            }
            for r in raw
        ]

    async def _product_performance(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        """Per-product sales vs purchases for report 162."""

        sales_rows, purchase_rows, products_list = await asyncio.gather(
            self._product_sale_by_product(company_id=company_id, criteria=criteria),
            self._product_purchase_by_product(company_id=company_id, criteria=criteria),
            self._db.product.find_many(where={"companyId": company_id}),
        )
        return await maybe_thread(
            _merge_product_performance,
            sales_rows,
            purchase_rows,
            products_list,
            min_rows=200,
            row_count=max(len(sales_rows), len(purchase_rows)),
        )

    async def _price_list(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        where = apply_asc_code_keyset(
            {"companyId": company_id, "isArchived": False},
            criteria=criteria,
            code_field="code",
        )
        page_size = page_size_from_criteria(criteria)
        rows = await self._db.product.find_many(
            where=where,
            order=[{"code": "asc"}, {"id": "asc"}],
            take=page_size + 1,
        )

        def _row(p: Any) -> dict:
            return {
                "code": p.code,
                "name": p.name,
                "salePrice": str(getattr(p, "salePrice", p.cost)),
                "cost": str(p.cost),
                "unit": str(getattr(p, "unit", "EA")),
            }

        out, next_cursor = trim_keyset_page_code(
            rows, page_size=page_size, to_dict=_row, code_field="code"
        )
        return attach_pagination_meta(out, criteria=criteria, next_cursor=next_cursor)

    async def _out_of_stock(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        qty_rows = await self._stock_quantity(company_id=company_id, criteria=criteria)
        return [r for r in qty_rows if Decimal(str(r.get("quantityOnHand", 0))) <= 0]

    async def _low_stock(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        threshold = Decimal(str(criteria.get("lowStockThreshold") or 10))
        qty_rows = await self._stock_quantity(company_id=company_id, criteria=criteria)
        out: list[dict] = []
        for r in qty_rows:
            qty = Decimal(str(r.get("quantityOnHand", 0)))
            if Decimal(0) < qty <= threshold:
                out.append({**r, "lowStockThreshold": str(threshold)})
        return out

    async def _purchase_bills_by_supplier(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        status, df, dt = self._sql_invoice_filters(criteria)
        raw = await self._db.query_raw(
            PURCHASE_SUMMARY_BY_SUPPLIER_SQL, company_id, status, df, dt
        )
        return [
            {"supplierId": r["supplierId"], "totalPurchases": str(r["totalPurchases"])}
            for r in raw
        ]

    async def _customer_outstanding_items(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        customer_id = criteria.get("customerId")
        if not customer_id:
            return [{"message": "customerId is required"}]
        lines = await self._customer_statement(
            company_id=company_id, criteria=criteria
        )
        return [
            line
            for line in lines
            if Decimal(str(line.get("balance", 0))) > 0
        ]

    async def _customer_products(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        customer_id = criteria.get("customerId")
        if not customer_id:
            return [{"message": "customerId is required"}]
        lines = await self._sales_invoice_line_detail(
            company_id=company_id,
            criteria={**criteria, "customerId": customer_id},
        )
        return await maybe_thread(
            _merge_customer_products,
            str(customer_id),
            lines,
            min_rows=200,
            row_count=len(lines),
        )

    async def _advanced_stock_quantity(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        product_code = criteria.get("productCode")
        product_filter = str(product_code) if product_code else None
        raw, products_list = await asyncio.gather(
            self._db.query_raw(
                ADVANCED_STOCK_BY_PRODUCT_SQL, company_id, product_filter
            ),
            self._db.product.find_many(where={"companyId": company_id}),
        )
        products = {p.code: p for p in products_list}
        out: list[dict] = []
        for row in raw:
            code = row["productCode"]
            qty = Decimal(str(row["quantityOnHand"]))
            prod = products.get(code)
            cost = prod.cost if prod else Decimal(0)
            expiry = row.get("nearestExpiry")
            out.append(
                {
                    "productCode": code,
                    "productName": prod.name if prod else None,
                    "batchCount": int(row.get("batchCount") or 0),
                    "quantityOnHand": str(qty),
                    "unitCost": str(cost),
                    "stockValue": str(qty * cost),
                    "nearestExpiry": (
                        expiry.isoformat()
                        if hasattr(expiry, "isoformat")
                        else (str(expiry) if expiry else None)
                    ),
                    "isStock": prod.isStock if prod else True,
                }
            )
        return out

    async def _multi_unit_price_list(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        where = apply_asc_code_keyset(
            {"companyId": company_id, "isArchived": False},
            criteria=criteria,
            code_field="code",
        )
        page_size = page_size_from_criteria(criteria)
        products = await self._db.product.find_many(
            where=where,
            order=[{"code": "asc"}, {"id": "asc"}],
            take=page_size + 1,
        )
        products = products[:page_size]
        product_ids = [p.id for p in products]
        uoms = (
            await self._db.productuom.find_many(
                where={"companyId": company_id, "productId": {"in": product_ids}},
            )
            if product_ids
            else []
        )
        by_product: dict[str, list] = {}
        for u in uoms:
            by_product.setdefault(u.productId, []).append(u)
        out: list[dict] = []
        for p in products:
            tiers = by_product.get(p.id)
            if not tiers:
                out.append(
                    {
                        "productCode": p.code,
                        "productName": p.name,
                        "unitCode": p.unit,
                        "conversionFactor": "1",
                        "salePrice": str(p.salePrice),
                        "isDefault": True,
                    }
                )
                continue
            for tier in tiers:
                out.append(
                    {
                        "productCode": p.code,
                        "productName": p.name,
                        "unitCode": tier.unitCode,
                        "conversionFactor": str(tier.conversionFactor),
                        "salePrice": str(tier.salePrice),
                        "isDefault": tier.isDefault,
                    }
                )
        return out

    async def _sale_summary_by_field(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        group_field = str(criteria.get("groupByField") or "productCode")
        if group_field.startswith("customFields."):
            return await self._sale_summary_by_custom_field(
                company_id=company_id, criteria=criteria, field_key=group_field.split(".", 1)[1]
            )
        lines = await self._sales_invoice_line_detail(
            company_id=company_id, criteria=criteria
        )
        totals: dict[str, Decimal] = {}
        counts: dict[str, int] = {}
        for line in lines:
            key = str(line.get(group_field) or line.get("productCode") or "—")
            totals[key] = totals.get(key, Decimal(0)) + Decimal(str(line.get("lineTotal", 0)))
            counts[key] = counts.get(key, 0) + 1
        return [
            {
                "groupByField": group_field,
                "fieldValue": key,
                "lineCount": counts[key],
                "totalSales": str(amount),
            }
            for key, amount in sorted(totals.items(), key=lambda x: -x[1])
        ]

    async def _sale_summary_by_custom_field(
        self, *, company_id: str, criteria: dict[str, Any], field_key: str
    ) -> list[dict]:
        status, df, dt = self._sql_invoice_filters(criteria)
        raw = await self._db.query_raw(
            SALE_SUMMARY_BY_CUSTOM_FIELD_SQL,
            company_id,
            status,
            df,
            dt,
            field_key,
        )
        return [
            {
                "groupByField": f"customFields.{field_key}",
                "fieldValue": r["fieldValue"],
                "invoiceCount": int(r["invoiceCount"]),
                "totalSales": str(r["totalSales"]),
            }
            for r in raw
        ]

    async def _customer_field_activity_summary(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        status, df, dt = self._sql_invoice_filters(criteria)
        raw = await self._db.query_raw(
            CUSTOMER_SALES_ACTIVITY_SQL, company_id, status, df, dt
        )
        return [
            {
                "customerId": r["customerId"],
                "customerCode": r.get("customerCode"),
                "customerName": r.get("customerName"),
                "invoiceCount": int(r["invoiceCount"]),
                "totalSales": str(r["totalSales"]),
                "lastInvoiceDate": (
                    r["lastInvoiceDate"].isoformat()
                    if hasattr(r["lastInvoiceDate"], "isoformat")
                    else str(r["lastInvoiceDate"])
                ),
            }
            for r in raw
        ]

    async def _bank_account_balances(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        _ = criteria
        _, dt = self._parse_dates(criteria)
        accounts, tb = await asyncio.gather(
            self._db.bankaccount.find_many(
                where={"companyId": company_id, "isActive": True}
            ),
            self._journals.trial_balance(company_id=company_id, as_of_date=dt),
        )
        by_code = {str(r.get("nominalCode")): r for r in tb if r.get("nominalCode")}
        out: list[dict] = []
        for acct in accounts:
            code = acct.nominalCode or ""
            row = by_code.get(code, {})
            balance = Decimal(str(row.get("balance", 0)))
            out.append(
                {
                    "bankAccountId": acct.id,
                    "name": acct.name,
                    "nominalCode": code,
                    "currency": acct.currency,
                    "balance": str(balance),
                }
            )
        return out

    async def _bank_cash_flow_monthly(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        df, dt = self._parse_dates(criteria)
        raw = await self._db.query_raw(
            BANK_CASH_FLOW_MONTHLY_SQL, company_id, df, dt
        )
        return [
            {
                "month": r["month"],
                "inflow": str(r["inflow"]),
                "outflow": str(r["outflow"]),
                "net": str(Decimal(str(r["inflow"])) - Decimal(str(r["outflow"]))),
            }
            for r in raw
        ]

    async def _assembly_job_cost_summary(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        where: dict[str, Any] = {"companyId": company_id}
        where = apply_desc_date_keyset(where, criteria=criteria, date_field="jobDate")
        page_size = page_size_from_criteria(criteria, maximum=500)
        jobs = await self._db.assemblyjob.find_many(
            where=where,
            order=[{"jobDate": "desc"}, {"id": "desc"}],
            take=page_size + 1,
        )
        page_jobs = jobs[:page_size]
        job_ids = [j.id for j in page_jobs]
        costs: dict[str, Decimal] = {}
        if job_ids:
            cost_rows = await self._db.query_raw(
                ASSEMBLY_JOB_LINE_COSTS_SQL, job_ids
            )
            costs = {
                str(r["jobId"]): Decimal(str(r["totalComponentCost"]))
                for r in cost_rows
            }
        out: list[dict] = []
        for job in page_jobs:
            out.append(
                {
                    "jobNumber": job.jobNumber,
                    "jobDate": job.jobDate.isoformat(),
                    "finishedProductCode": job.finishedProductCode,
                    "quantity": str(job.quantity),
                    "status": job.status,
                    "totalComponentCost": str(costs.get(job.id, Decimal(0))),
                }
            )
        if len(jobs) > page_size:
            last = page_jobs[-1]
            out.append(
                {
                    "_meta": {
                        "hasMore": True,
                        "nextCursor": {
                            "cursorDate": last.jobDate.isoformat(),
                            "cursorId": last.id,
                        },
                    }
                }
            )
        return out

    async def _project_payments_report(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        df, dt = self._parse_dates(criteria)
        raw = await self._db.query_raw(
            PROJECT_PAYMENTS_BY_CODE_SQL, company_id, df, dt
        )
        return [
            {
                "projectCode": r["projectCode"],
                "totalPayments": str(r["totalPayments"]),
            }
            for r in raw
        ]

    async def _financial_monthly_balances(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        """Twelve-month income vs expense totals (dashboard FIN_MTB)."""

        df, dt = self._parse_dates(criteria)
        rows = await self._journals.classified_balances(
            company_id=company_id, date_from=df, date_to=dt
        )
        income = sum(
            Decimal(str(r.get("balance", 0)))
            for r in rows
            if r.get("categoryType") == "Income"
        )
        expense = sum(
            Decimal(str(r.get("balance", 0)))
            for r in rows
            if r.get("categoryType") == "Expense"
        )
        return [
            {
                "periodFrom": criteria.get("dateFrom"),
                "periodTo": criteria.get("dateTo"),
                "totalIncome": str(income),
                "totalExpense": str(expense),
                "netProfit": str(income - expense),
            }
        ]

    async def _bank_receipts_list(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        df, dt = self._parse_dates(criteria)
        where: dict = {"companyId": company_id}
        if df or dt:
            rng: dict = {}
            if df:
                rng["gte"] = df
            if dt:
                rng["lte"] = dt
            where["receiptDate"] = rng
        where = apply_desc_date_keyset(where, criteria=criteria, date_field="receiptDate")
        page_size = page_size_from_criteria(criteria)
        rows = await self._db.bankreceipt.find_many(
            where=where,
            order=[{"receiptDate": "desc"}, {"id": "desc"}],
            take=page_size + 1,
        )

        def _row(r: Any) -> dict:
            return {
                "id": r.id,
                "voucherNumber": r.voucherNumber,
                "receiptDate": r.receiptDate.isoformat(),
                "bankAccountId": r.bankAccountId,
                "totalAmount": str(r.totalAmount),
                "direction": "in",
            }

        out, next_cursor = trim_keyset_page(
            rows, page_size=page_size, to_dict=_row, date_field="receiptDate"
        )
        return attach_pagination_meta(out, criteria=criteria, next_cursor=next_cursor)

    async def _bank_transfers_list(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        df, dt = self._parse_dates(criteria)
        where: dict = {"companyId": company_id}
        if df or dt:
            rng: dict = {}
            if df:
                rng["gte"] = df
            if dt:
                rng["lte"] = dt
            where["transferDate"] = rng
        where = apply_desc_date_keyset(where, criteria=criteria, date_field="transferDate")
        page_size = page_size_from_criteria(criteria)
        rows = await self._db.banktransfer.find_many(
            where=where,
            order=[{"transferDate": "desc"}, {"id": "desc"}],
            take=page_size + 1,
        )

        def _row(t: Any) -> dict:
            return {
                "id": t.id,
                "voucherNumber": t.voucherNumber,
                "transferDate": t.transferDate.isoformat(),
                "fromBankAccountId": t.fromBankAccountId,
                "toBankAccountId": t.toBankAccountId,
                "amount": str(t.totalAmount),
            }

        out, next_cursor = trim_keyset_page(
            rows, page_size=page_size, to_dict=_row, date_field="transferDate"
        )
        return attach_pagination_meta(out, criteria=criteria, next_cursor=next_cursor)

    async def _bank_activity_summary(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        payments, receipts = await asyncio.gather(
            self._bank_payments(company_id=company_id, criteria=criteria),
            self._bank_receipts_list(company_id=company_id, criteria=criteria),
        )
        pay_rows = [p for p in payments if "_meta" not in p]
        rec_rows = [r for r in receipts if "_meta" not in r]
        total_out = sum(Decimal(str(p.get("amount", 0))) for p in pay_rows)
        total_in = sum(Decimal(str(r.get("totalAmount", 0))) for r in rec_rows)
        return [
            {
                "paymentCount": len(pay_rows),
                "receiptCount": len(rec_rows),
                "totalOutflow": str(total_out),
                "totalInflow": str(total_in),
                "netCash": str(total_in - total_out),
            }
        ]

    async def _assembly_templates_list(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        _ = criteria
        raw = await self._db.query_raw(ASSEMBLY_TEMPLATE_SUMMARY_SQL, company_id)
        return [
            {
                "code": r["code"],
                "name": r["name"],
                "finishedProductCode": r["finishedProductCode"],
                "componentCount": int(r["componentCount"]),
            }
            for r in raw
        ]

    def _month_window(
        self, *, anchor: datetime, months_ago: int
    ) -> tuple[datetime, datetime]:
        tz = anchor.tzinfo or timezone.utc
        year = anchor.year
        month = anchor.month - months_ago
        while month <= 0:
            month += 12
            year -= 1
        last_day = monthrange(year, month)[1]
        start = datetime(year, month, 1, tzinfo=tz)
        end = datetime(year, month, last_day, 23, 59, 59, tzinfo=tz)
        return start, end

    async def _financial_comparative_pnl(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        """Multi-period income / expense / net by calendar month — P13."""

        _, dt = self._parse_dates(criteria)
        anchor = dt or datetime.now(timezone.utc)
        period_count = min(max(1, int(criteria.get("periodCount") or 12)), 36)
        return await self._journals.monthly_classified_pnl(
            company_id=company_id,
            anchor=anchor,
            period_count=period_count,
        )

    async def _financial_comparative_pnl_by_category(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        """Income/expense per month and COA category — P14."""

        _, dt = self._parse_dates(criteria)
        anchor = dt or datetime.now(timezone.utc)
        period_count = min(max(1, int(criteria.get("periodCount") or 12)), 36)
        return await self._journals.monthly_classified_pnl_by_category(
            company_id=company_id,
            anchor=anchor,
            period_count=period_count,
        )

    async def _financial_trial_balance_by_month(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        """Month-end trial balance totals (debit/credit/net) — P15."""

        _, dt = self._parse_dates(criteria)
        anchor = dt or datetime.now(timezone.utc)
        period_count = min(max(1, int(criteria.get("periodCount") or 12)), 36)
        return await self._journals.monthly_tb_totals(
            company_id=company_id,
            anchor=anchor,
            period_count=period_count,
        )

    async def _assembly_wip_jobs(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        where: dict[str, Any] = {
            "companyId": company_id,
            "status": {"not": "finished"},
        }
        where = apply_desc_date_keyset(where, criteria=criteria, date_field="jobDate")
        page_size = page_size_from_criteria(criteria, maximum=500)
        jobs = await self._db.assemblyjob.find_many(
            where=where,
            order=[{"jobDate": "desc"}, {"id": "desc"}],
            take=page_size + 1,
        )
        jobs = jobs[:page_size]
        return [
            {
                "jobNumber": j.jobNumber,
                "jobDate": j.jobDate.isoformat(),
                "finishedProductCode": j.finishedProductCode,
                "quantity": str(j.quantity),
                "status": j.status,
            }
            for j in jobs
        ]

    async def _assembly_component_cost_detail(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict]:
        df, dt, cursor_date, cursor_id = self._sql_date_keyset_params(criteria)
        page_size = page_size_from_criteria(criteria, maximum=2000)
        raw = await self._db.query_raw(
            ASSEMBLY_COMPONENT_DETAIL_SQL,
            company_id,
            df,
            dt,
            cursor_date,
            cursor_id,
            page_size + 1,
        )
        has_more = len(raw) > page_size
        if has_more:
            raw = raw[:page_size]
        out = [
            {
                "jobNumber": r["jobNumber"],
                "finishedProductCode": r["finishedProductCode"],
                "componentProductCode": r["componentProductCode"],
                "quantity": str(r["quantity"]),
                "unitCost": str(r["unitCost"]),
                "lineCost": str(r["lineCost"]),
            }
            for r in raw
        ]
        next_cursor = None
        if has_more and raw:
            last = raw[-1]
            job_date = last["jobDate"]
            next_cursor = {
                "cursorDate": (
                    job_date.isoformat()
                    if hasattr(job_date, "isoformat")
                    else str(job_date)
                ),
                "cursorId": last["jobId"],
                "hasMore": True,
            }
        return attach_pagination_meta(out, criteria=criteria, next_cursor=next_cursor)

    async def _budget_vs_actual(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict[str, Any]]:
        budget_id = criteria.get("budgetId") or criteria.get("budget_id")
        if not budget_id:
            return []
        budget = await self._db.budget.find_first(
            where={"id": str(budget_id), "companyId": company_id},
            include={"lines": True},
        )
        if budget is None:
            return []

        date_from = self._criteria_date(criteria, "dateFrom", "date_from")
        date_to = self._criteria_date(criteria, "dateTo", "date_to", end_of_day=True)
        actual_rows = await self._db.query_raw(
            BUDGET_ACTUAL_BY_NOMINAL_SQL, company_id, date_from, date_to
        )
        actual_by_nominal = {
            str(r["nominalCode"]): Decimal(str(r["actual"])) for r in actual_rows
        }

        rows: list[dict[str, Any]] = []
        for bl in budget.lines or []:
            code = str(bl.nominalCode)
            budget_amt = Decimal(str(bl.amount))
            actual = actual_by_nominal.get(code, Decimal(0))
            rows.append(
                {
                    "nominalCode": code,
                    "period": bl.period,
                    "budgetAmount": str(budget_amt),
                    "actualAmount": str(actual),
                    "variance": str(actual - budget_amt),
                }
            )
        return rows

    async def _ar_aging_report(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict[str, Any]]:
        as_of = self._criteria_date(criteria, "asOfDate", "as_of_date", end_of_day=True)
        if as_of is None:
            as_of = self._criteria_date(criteria, "dateTo", "date_to", end_of_day=True)
        result = await self._aging.ar_aging(company_id=company_id, as_of_date=as_of)
        return list(result.get("rows") or [])

    async def _ap_aging_report(
        self, *, company_id: str, criteria: dict[str, Any]
    ) -> list[dict[str, Any]]:
        as_of = self._criteria_date(criteria, "asOfDate", "as_of_date", end_of_day=True)
        if as_of is None:
            as_of = self._criteria_date(criteria, "dateTo", "date_to", end_of_day=True)
        result = await self._aging.ap_aging(company_id=company_id, as_of_date=as_of)
        return list(result.get("rows") or [])

    def _criteria_date(
        self,
        criteria: dict[str, Any],
        *keys: str,
        end_of_day: bool = False,
    ) -> datetime | None:
        from app.services.activity_filters import parse_activity_date

        for key in keys:
            raw = criteria.get(key)
            if raw:
                return parse_activity_date(str(raw), end_of_day=end_of_day)
        return None
