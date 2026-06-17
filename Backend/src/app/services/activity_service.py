"""Unified sales / purchase activity lists — FastAccounts Sales All / Purchases All."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

from prisma_generated import Prisma

from app.services.activity_filters import (
    activity_where,
    filter_activity_rows,
    parse_activity_date,
)

# Cap rows per source table — keeps activity feeds under SLA without unbounded scans.
ACTIVITY_FETCH_LIMIT = 500

SALES_CORE_TYPES = {
    "Sale Invoice": "invoice",
    "Sale Receipt": "receipt",
    "Sale Credit": "credit",
}
SALES_PLANNING_TYPES = {
    "Quotation": "quotation",
    "Sales Order": "sales_order",
    "PDC Received": "pdc_received",
    "Delivery Note": "delivery_note",
}
PURCHASES_CORE_TYPES = {
    "Purchase Invoice": "bill",
    "Supplier Payment": "payment",
    "Supplier Credit": "credit",
}
PURCHASES_PLANNING_TYPES = {
    "Purchase Order": "purchase_order",
    "PDC Issued": "pdc_issued",
    "GRN": "grn",
}


class ActivityService:
    """Merge transactional documents into FA-style activity feeds."""

    def __init__(self, prisma: Prisma) -> None:
        self._db = prisma

    async def list_sales_activity(
        self,
        *,
        company_id: str,
        include_planning: bool = False,
        date_from: str | None = None,
        date_to: str | None = None,
        party_id: str | None = None,
        doc_type: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        dt_from = parse_activity_date(date_from)
        dt_to = parse_activity_date(date_to, end_of_day=True)
        types = {**SALES_CORE_TYPES}
        if include_planning:
            types.update(SALES_PLANNING_TYPES)
        if doc_type:
            if doc_type not in types:
                return []
            types = {doc_type: types[doc_type]}

        rows: list[dict[str, Any]] = []
        tasks: list[Any] = []
        party_field = "customerId"

        if "invoice" in types.values():
            tasks.append(
                self._db.salesinvoice.find_many(
                    where=activity_where(
                        company_id=company_id,
                        party_field=party_field,
                        date_field="invoiceDate",
                        party_id=party_id,
                        date_from=dt_from,
                        date_to=dt_to,
                        status=status,
                    ),
                    order={"invoiceDate": "desc"},
                    take=ACTIVITY_FETCH_LIMIT,
                )
            )
        else:
            tasks.append(_empty_list())

        if "receipt" in types.values():
            tasks.append(
                self._db.salesreceipt.find_many(
                    where=activity_where(
                        company_id=company_id,
                        party_field=party_field,
                        date_field="receiptDate",
                        party_id=party_id,
                        date_from=dt_from,
                        date_to=dt_to,
                        status=status,
                    ),
                    order={"receiptDate": "desc"},
                    take=ACTIVITY_FETCH_LIMIT,
                )
            )
        else:
            tasks.append(_empty_list())

        if "credit" in types.values():
            tasks.append(
                self._db.salescredit.find_many(
                    where=activity_where(
                        company_id=company_id,
                        party_field=party_field,
                        date_field="creditDate",
                        party_id=party_id,
                        date_from=dt_from,
                        date_to=dt_to,
                        status=status,
                    ),
                    order={"creditDate": "desc"},
                    take=ACTIVITY_FETCH_LIMIT,
                )
            )
        else:
            tasks.append(_empty_list())

        if include_planning:
            keys = list(types.values())
            if "quotation" in keys:
                tasks.append(
                    self._db.quotation.find_many(
                        where=activity_where(
                            company_id=company_id,
                            party_field=party_field,
                            date_field="quotationDate",
                            party_id=party_id,
                            date_from=dt_from,
                            date_to=dt_to,
                            status=status,
                        ),
                        order={"quotationDate": "desc"},
                        take=ACTIVITY_FETCH_LIMIT,
                    )
                )
            else:
                tasks.append(_empty_list())
            if "sales_order" in keys:
                tasks.append(
                    self._db.salesorder.find_many(
                        where=activity_where(
                            company_id=company_id,
                            party_field=party_field,
                            date_field="orderDate",
                            party_id=party_id,
                            date_from=dt_from,
                            date_to=dt_to,
                            status=status,
                        ),
                        order={"orderDate": "desc"},
                        take=ACTIVITY_FETCH_LIMIT,
                    )
                )
            else:
                tasks.append(_empty_list())
            if "pdc_received" in keys:
                tasks.append(
                    self._db.postdatedchequereceived.find_many(
                        where=activity_where(
                            company_id=company_id,
                            party_field=party_field,
                            date_field="receivedDate",
                            party_id=party_id,
                            date_from=dt_from,
                            date_to=dt_to,
                            status=status,
                        ),
                        order={"receivedDate": "desc"},
                        take=ACTIVITY_FETCH_LIMIT,
                    )
                )
            else:
                tasks.append(_empty_list())
            if "delivery_note" in keys:
                tasks.append(
                    self._db.deliverynote.find_many(
                        where=activity_where(
                            company_id=company_id,
                            party_field=party_field,
                            date_field="deliveryDate",
                            party_id=party_id,
                            date_from=dt_from,
                            date_to=dt_to,
                            status=status,
                        ),
                        order={"deliveryDate": "desc"},
                        take=ACTIVITY_FETCH_LIMIT,
                    )
                )
            else:
                tasks.append(_empty_list())

        results = await asyncio.gather(*tasks)
        invoices, receipts, credits = results[0], results[1], results[2]

        for inv in invoices:
            rows.append(_sales_invoice_row(inv))
        for rcpt in receipts:
            rows.append(_sales_receipt_row(rcpt))
        for cr in credits:
            rows.append(_sales_credit_row(cr))

        if include_planning:
            quotations, orders, pdc, delivery_notes = results[3], results[4], results[5], results[6]
            rows.extend(
                self._sales_planning_rows(quotations, orders, pdc, delivery_notes)
            )

        rows.sort(key=lambda r: r["documentDate"], reverse=True)
        return filter_activity_rows(rows, doc_type=doc_type, status=status)

    def _sales_planning_rows(
        self,
        quotations: list[Any],
        orders: list[Any],
        pdc: list[Any],
        delivery_notes: list[Any],
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for q in quotations:
            rows.append(
                {
                    "entityType": "quotation",
                    "entityId": q.id,
                    "docType": "Quotation",
                    "documentNumber": q.quotationNumber,
                    "documentDate": q.quotationDate.isoformat(),
                    "partyId": q.customerId,
                    "partyKind": "customer",
                    **_party_fields(q, kind="customer"),
                    "totalAmount": str(q.totalAmount),
                    "status": q.status,
                }
            )
        for so in orders:
            rows.append(
                {
                    "entityType": "sales_order",
                    "entityId": so.id,
                    "docType": "Sales Order",
                    "documentNumber": so.orderNumber,
                    "documentDate": so.orderDate.isoformat(),
                    "partyId": so.customerId,
                    "partyKind": "customer",
                    **_party_fields(so, kind="customer"),
                    "totalAmount": str(so.totalAmount),
                    "status": so.status,
                }
            )
        for p in pdc:
            rows.append(
                {
                    "entityType": "pdc_received",
                    "entityId": p.id,
                    "docType": "PDC Received",
                    "documentNumber": p.voucherNumber,
                    "documentDate": p.receivedDate.isoformat(),
                    "partyId": p.customerId,
                    "partyKind": "customer",
                    **_party_fields(p, kind="customer"),
                    "totalAmount": str(p.amount),
                    "status": p.status,
                }
            )
        for dn in delivery_notes:
            rows.append(
                {
                    "entityType": "delivery_note",
                    "entityId": dn.id,
                    "docType": "Delivery Note",
                    "documentNumber": dn.voucherNumber,
                    "documentDate": dn.deliveryDate.isoformat(),
                    "partyId": dn.customerId,
                    "partyKind": "customer",
                    **_party_fields(dn, kind="customer"),
                    "totalAmount": "0",
                    "status": dn.status,
                }
            )
        return rows

    async def _fetch_sales_planning(
        self,
        *,
        company_id: str,
        types: dict[str, str],
        party_id: str | None,
        dt_from: datetime | None,
        dt_to: datetime | None,
        status: str | None,
    ) -> list[dict[str, Any]]:
        party_field = "customerId"
        tasks: list[Any] = []
        keys = list(types.values())

        if "quotation" in keys:
            tasks.append(
                self._db.quotation.find_many(
                    where=activity_where(
                        company_id=company_id,
                        party_field=party_field,
                        date_field="quotationDate",
                        party_id=party_id,
                        date_from=dt_from,
                        date_to=dt_to,
                        status=status,
                    ),
                    order={"quotationDate": "desc"},
                    take=ACTIVITY_FETCH_LIMIT,
                )
            )
        else:
            tasks.append(_empty_list())

        if "sales_order" in keys:
            tasks.append(
                self._db.salesorder.find_many(
                    where=activity_where(
                        company_id=company_id,
                        party_field=party_field,
                        date_field="orderDate",
                        party_id=party_id,
                        date_from=dt_from,
                        date_to=dt_to,
                        status=status,
                    ),
                    order={"orderDate": "desc"},
                    take=ACTIVITY_FETCH_LIMIT,
                )
            )
        else:
            tasks.append(_empty_list())

        if "pdc_received" in keys:
            tasks.append(
                self._db.postdatedchequereceived.find_many(
                    where=activity_where(
                        company_id=company_id,
                        party_field=party_field,
                        date_field="receivedDate",
                        party_id=party_id,
                        date_from=dt_from,
                        date_to=dt_to,
                        status=status,
                    ),
                    order={"receivedDate": "desc"},
                    take=ACTIVITY_FETCH_LIMIT,
                )
            )
        else:
            tasks.append(_empty_list())

        if "delivery_note" in keys:
            tasks.append(
                self._db.deliverynote.find_many(
                    where=activity_where(
                        company_id=company_id,
                        party_field=party_field,
                        date_field="deliveryDate",
                        party_id=party_id,
                        date_from=dt_from,
                        date_to=dt_to,
                        status=status,
                    ),
                    order={"deliveryDate": "desc"},
                    take=ACTIVITY_FETCH_LIMIT,
                )
            )
        else:
            tasks.append(_empty_list())

        quotations, orders, pdc, delivery_notes = await asyncio.gather(*tasks)
        rows: list[dict[str, Any]] = []
        for q in quotations:
            rows.append(
                {
                    "entityType": "quotation",
                    "entityId": q.id,
                    "docType": "Quotation",
                    "documentNumber": q.quotationNumber,
                    "documentDate": q.quotationDate.isoformat(),
                    "partyId": q.customerId,
                    "partyKind": "customer",
                    **_party_fields(q, kind="customer"),
                    "totalAmount": str(q.totalAmount),
                    "status": q.status,
                }
            )
        for so in orders:
            rows.append(
                {
                    "entityType": "sales_order",
                    "entityId": so.id,
                    "docType": "Sales Order",
                    "documentNumber": so.orderNumber,
                    "documentDate": so.orderDate.isoformat(),
                    "partyId": so.customerId,
                    "partyKind": "customer",
                    **_party_fields(so, kind="customer"),
                    "totalAmount": str(so.totalAmount),
                    "status": so.status,
                }
            )
        for p in pdc:
            rows.append(
                {
                    "entityType": "pdc_received",
                    "entityId": p.id,
                    "docType": "PDC Received",
                    "documentNumber": p.voucherNumber,
                    "documentDate": p.receivedDate.isoformat(),
                    "partyId": p.customerId,
                    "partyKind": "customer",
                    **_party_fields(p, kind="customer"),
                    "totalAmount": str(p.amount),
                    "status": p.status,
                }
            )
        for dn in delivery_notes:
            rows.append(
                {
                    "entityType": "delivery_note",
                    "entityId": dn.id,
                    "docType": "Delivery Note",
                    "documentNumber": dn.voucherNumber,
                    "documentDate": dn.deliveryDate.isoformat(),
                    "partyId": dn.customerId,
                    "partyKind": "customer",
                    **_party_fields(dn, kind="customer"),
                    "totalAmount": "0",
                    "status": dn.status,
                }
            )
        return rows

    async def list_purchases_activity(
        self,
        *,
        company_id: str,
        include_planning: bool = False,
        date_from: str | None = None,
        date_to: str | None = None,
        party_id: str | None = None,
        doc_type: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        dt_from = parse_activity_date(date_from)
        dt_to = parse_activity_date(date_to, end_of_day=True)
        types = {**PURCHASES_CORE_TYPES}
        if include_planning:
            types.update(PURCHASES_PLANNING_TYPES)
        if doc_type:
            if doc_type not in types:
                return []
            types = {doc_type: types[doc_type]}

        rows: list[dict[str, Any]] = []
        tasks: list[Any] = []
        party_field = "supplierId"

        if "bill" in types.values():
            tasks.append(
                self._db.supplierbill.find_many(
                    where=activity_where(
                        company_id=company_id,
                        party_field=party_field,
                        date_field="billDate",
                        party_id=party_id,
                        date_from=dt_from,
                        date_to=dt_to,
                        status=status,
                    ),
                    order={"billDate": "desc"},
                    take=ACTIVITY_FETCH_LIMIT,
                )
            )
        else:
            tasks.append(_empty_list())

        if "payment" in types.values():
            tasks.append(
                self._db.supplierpayment.find_many(
                    where=activity_where(
                        company_id=company_id,
                        party_field=party_field,
                        date_field="paymentDate",
                        party_id=party_id,
                        date_from=dt_from,
                        date_to=dt_to,
                        status=status,
                    ),
                    order={"paymentDate": "desc"},
                    take=ACTIVITY_FETCH_LIMIT,
                )
            )
        else:
            tasks.append(_empty_list())

        if "credit" in types.values():
            tasks.append(
                self._db.suppliercredit.find_many(
                    where=activity_where(
                        company_id=company_id,
                        party_field=party_field,
                        date_field="creditDate",
                        party_id=party_id,
                        date_from=dt_from,
                        date_to=dt_to,
                        status=status,
                    ),
                    order={"creditDate": "desc"},
                    take=ACTIVITY_FETCH_LIMIT,
                )
            )
        else:
            tasks.append(_empty_list())

        if include_planning:
            keys = list(types.values())
            if "purchase_order" in keys:
                tasks.append(
                    self._db.purchaseorder.find_many(
                        where=activity_where(
                            company_id=company_id,
                            party_field=party_field,
                            date_field="orderDate",
                            party_id=party_id,
                            date_from=dt_from,
                            date_to=dt_to,
                            status=status,
                        ),
                        order={"orderDate": "desc"},
                        take=ACTIVITY_FETCH_LIMIT,
                    )
                )
            else:
                tasks.append(_empty_list())
            if "pdc_issued" in keys:
                tasks.append(
                    self._db.postdatedchequeissued.find_many(
                        where=activity_where(
                            company_id=company_id,
                            party_field=party_field,
                            date_field="issuedDate",
                            party_id=party_id,
                            date_from=dt_from,
                            date_to=dt_to,
                            status=status,
                        ),
                        order={"issuedDate": "desc"},
                        take=ACTIVITY_FETCH_LIMIT,
                    )
                )
            else:
                tasks.append(_empty_list())
            if "grn" in keys:
                tasks.append(
                    self._db.goodsreceiptnote.find_many(
                        where=activity_where(
                            company_id=company_id,
                            party_field=party_field,
                            date_field="receiptDate",
                            party_id=party_id,
                            date_from=dt_from,
                            date_to=dt_to,
                            status=status,
                        ),
                        order={"receiptDate": "desc"},
                        take=ACTIVITY_FETCH_LIMIT,
                    )
                )
            else:
                tasks.append(_empty_list())

        results = await asyncio.gather(*tasks)
        bills, payments, credits = results[0], results[1], results[2]

        for bill in bills:
            rows.append(_purchase_bill_row(bill))
        for pay in payments:
            rows.append(_purchase_payment_row(pay))
        for cr in credits:
            rows.append(_purchase_credit_row(cr))

        if include_planning:
            purchase_orders, pdc_issued, grns = results[3], results[4], results[5]
            rows.extend(
                self._purchases_planning_rows(purchase_orders, pdc_issued, grns)
            )

        rows.sort(key=lambda r: r["documentDate"], reverse=True)
        return filter_activity_rows(rows, doc_type=doc_type, status=status)

    def _purchases_planning_rows(
        self,
        purchase_orders: list[Any],
        pdc_issued: list[Any],
        grns: list[Any],
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for po in purchase_orders:
            rows.append(
                {
                    "entityType": "purchase_order",
                    "entityId": po.id,
                    "docType": "Purchase Order",
                    "documentNumber": po.orderNumber,
                    "documentDate": po.orderDate.isoformat(),
                    "partyId": po.supplierId,
                    "partyKind": "supplier",
                    **_party_fields(po, kind="supplier"),
                    "totalAmount": str(po.totalAmount),
                    "status": po.status,
                }
            )
        for p in pdc_issued:
            rows.append(
                {
                    "entityType": "pdc_issued",
                    "entityId": p.id,
                    "docType": "PDC Issued",
                    "documentNumber": p.voucherNumber,
                    "documentDate": p.issuedDate.isoformat(),
                    "partyId": p.supplierId,
                    "partyKind": "supplier",
                    **_party_fields(p, kind="supplier"),
                    "totalAmount": str(p.amount),
                    "status": p.status,
                }
            )
        for grn in grns:
            rows.append(
                {
                    "entityType": "grn",
                    "entityId": grn.id,
                    "docType": "GRN",
                    "documentNumber": grn.voucherNumber,
                    "documentDate": grn.receiptDate.isoformat(),
                    "partyId": grn.supplierId,
                    "partyKind": "supplier",
                    **_party_fields(grn, kind="supplier"),
                    "totalAmount": "0",
                    "status": grn.status,
                }
            )
        return rows

    async def _fetch_purchases_planning(
        self,
        *,
        company_id: str,
        types: dict[str, str],
        party_id: str | None,
        dt_from: datetime | None,
        dt_to: datetime | None,
        status: str | None,
    ) -> list[dict[str, Any]]:
        party_field = "supplierId"
        tasks: list[Any] = []
        keys = list(types.values())

        if "purchase_order" in keys:
            tasks.append(
                self._db.purchaseorder.find_many(
                    where=activity_where(
                        company_id=company_id,
                        party_field=party_field,
                        date_field="orderDate",
                        party_id=party_id,
                        date_from=dt_from,
                        date_to=dt_to,
                        status=status,
                    ),
                    order={"orderDate": "desc"},
                    take=ACTIVITY_FETCH_LIMIT,
                )
            )
        else:
            tasks.append(_empty_list())

        if "pdc_issued" in keys:
            tasks.append(
                self._db.postdatedchequeissued.find_many(
                    where=activity_where(
                        company_id=company_id,
                        party_field=party_field,
                        date_field="issuedDate",
                        party_id=party_id,
                        date_from=dt_from,
                        date_to=dt_to,
                        status=status,
                    ),
                    order={"issuedDate": "desc"},
                    take=ACTIVITY_FETCH_LIMIT,
                )
            )
        else:
            tasks.append(_empty_list())

        if "grn" in keys:
            tasks.append(
                self._db.goodsreceiptnote.find_many(
                    where=activity_where(
                        company_id=company_id,
                        party_field=party_field,
                        date_field="receiptDate",
                        party_id=party_id,
                        date_from=dt_from,
                        date_to=dt_to,
                        status=status,
                    ),
                    order={"receiptDate": "desc"},
                    take=ACTIVITY_FETCH_LIMIT,
                )
            )
        else:
            tasks.append(_empty_list())

        orders, pdc, grns = await asyncio.gather(*tasks)
        rows: list[dict[str, Any]] = []
        for po in orders:
            rows.append(
                {
                    "entityType": "purchase_order",
                    "entityId": po.id,
                    "docType": "Purchase Order",
                    "documentNumber": po.orderNumber,
                    "documentDate": po.orderDate.isoformat(),
                    "partyId": po.supplierId,
                    "partyKind": "supplier",
                    **_party_fields(po, kind="supplier"),
                    "totalAmount": str(po.totalAmount),
                    "status": po.status,
                }
            )
        for p in pdc:
            rows.append(
                {
                    "entityType": "pdc_issued",
                    "entityId": p.id,
                    "docType": "PDC Issued",
                    "documentNumber": p.voucherNumber,
                    "documentDate": p.issuedDate.isoformat(),
                    "partyId": p.supplierId,
                    "partyKind": "supplier",
                    **_party_fields(p, kind="supplier"),
                    "totalAmount": str(p.amount),
                    "status": p.status,
                }
            )
        for grn in grns:
            rows.append(
                {
                    "entityType": "grn",
                    "entityId": grn.id,
                    "docType": "GRN",
                    "documentNumber": grn.voucherNumber,
                    "documentDate": grn.receiptDate.isoformat(),
                    "partyId": grn.supplierId,
                    "partyKind": "supplier",
                    **_party_fields(grn, kind="supplier"),
                    "totalAmount": "0",
                    "status": grn.status,
                }
            )
        return rows


async def _empty_list() -> list[Any]:
    return []


def _party_fields(row: Any, *, kind: str) -> dict[str, str | None]:
    if kind == "customer":
        return {
            "partyCode": getattr(row, "customerCode", None),
            "partyName": getattr(row, "customerName", None),
        }
    return {
        "partyCode": getattr(row, "supplierCode", None),
        "partyName": getattr(row, "supplierName", None),
    }


def _sales_invoice_row(inv: Any) -> dict[str, Any]:
    return {
        "entityType": "invoice",
        "entityId": inv.id,
        "docType": "Sale Invoice",
        "documentNumber": inv.invoiceNumber,
        "documentDate": inv.invoiceDate.isoformat(),
        "partyId": inv.customerId,
        "partyKind": "customer",
        **_party_fields(inv, kind="customer"),
        "totalAmount": str(inv.totalAmount),
        "status": inv.status,
    }


def _sales_receipt_row(rcpt: Any) -> dict[str, Any]:
    return {
        "entityType": "receipt",
        "entityId": rcpt.id,
        "docType": "Sale Receipt",
        "documentNumber": rcpt.receiptNumber,
        "documentDate": rcpt.receiptDate.isoformat(),
        "partyId": rcpt.customerId,
        "partyKind": "customer",
        **_party_fields(rcpt, kind="customer"),
        "totalAmount": str(rcpt.totalAmount),
        "status": rcpt.status,
    }


def _sales_credit_row(cr: Any) -> dict[str, Any]:
    return {
        "entityType": "credit",
        "entityId": cr.id,
        "docType": "Sale Credit",
        "documentNumber": cr.creditNumber,
        "documentDate": cr.creditDate.isoformat(),
        "partyId": cr.customerId,
        "partyKind": "customer",
        **_party_fields(cr, kind="customer"),
        "totalAmount": str(cr.totalAmount),
        "status": cr.status,
    }


def _purchase_bill_row(bill: Any) -> dict[str, Any]:
    return {
        "entityType": "bill",
        "entityId": bill.id,
        "docType": "Purchase Invoice",
        "documentNumber": bill.billNumber,
        "documentDate": bill.billDate.isoformat(),
        "partyId": bill.supplierId,
        "partyKind": "supplier",
        **_party_fields(bill, kind="supplier"),
        "totalAmount": str(bill.totalAmount),
        "status": bill.status,
    }


def _purchase_payment_row(pay: Any) -> dict[str, Any]:
    return {
        "entityType": "payment",
        "entityId": pay.id,
        "docType": "Supplier Payment",
        "documentNumber": pay.voucherNumber,
        "documentDate": pay.paymentDate.isoformat(),
        "partyId": pay.supplierId,
        "partyKind": "supplier",
        **_party_fields(pay, kind="supplier"),
        "totalAmount": str(pay.totalAmount),
        "status": pay.status,
    }


def _purchase_credit_row(cr: Any) -> dict[str, Any]:
    return {
        "entityType": "credit",
        "entityId": cr.id,
        "docType": "Supplier Credit",
        "documentNumber": cr.creditNumber,
        "documentDate": cr.creditDate.isoformat(),
        "partyId": cr.supplierId,
        "partyKind": "supplier",
        **_party_fields(cr, kind="supplier"),
        "totalAmount": str(cr.totalAmount),
        "status": cr.status,
    }
