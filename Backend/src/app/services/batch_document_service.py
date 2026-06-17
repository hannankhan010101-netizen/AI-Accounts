"""Batch sales invoice / supplier bill entry — FA §3.9."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import Any

from app.core.exceptions import ValidationAppError
from app.repositories.sales_invoice_repository import SalesInvoiceRepository
from app.repositories.supplier_bill_repository import SupplierBillRepository
from app.services.document_number_service import DocumentNumberService
from app.services.lock_date_service import LockDateService
from app.services.tax_calculation_service import TaxCalculationService
from app.utils.line_description import merge_line_description_fields
from app.utils.smart_filters import smart_filters_custom_fields


class BatchDocumentService:
    def __init__(
        self,
        *,
        sales_invoice_repository: SalesInvoiceRepository,
        supplier_bill_repository: SupplierBillRepository,
        document_number_service: DocumentNumberService,
        lock_date_service: LockDateService,
        tax_service: TaxCalculationService,
    ) -> None:
        self._sales_invoices = sales_invoice_repository
        self._supplier_bills = supplier_bill_repository
        self._numbers = document_number_service
        self._lock_date = lock_date_service
        self._tax = tax_service

    async def create_batch_sales_invoices(
        self,
        *,
        company_id: str,
        invoice_date: datetime,
        entries: list[Any],
        smart_filters: dict[str, str] | None = None,
        prisma: Any | None = None,
    ) -> dict[str, Any]:
        if not entries:
            raise ValidationAppError("At least one batch row is required")

        await self._lock_date.assert_not_locked(
            company_id=company_id,
            document_date=invoice_date,
            document_label="sales invoice",
        )

        grouped: dict[str, list[Any]] = defaultdict(list)
        for entry in entries:
            party_id = str(getattr(entry, "customer_id", "") or "").strip()
            if not party_id:
                raise ValidationAppError("Each batch row requires a customer")
            grouped[party_id].append(entry)

        custom_fields = smart_filters_custom_fields(smart_filters)
        created: list[dict[str, Any]] = []

        for customer_id, party_entries in grouped.items():
            raw_lines: list[dict[str, Any]] = []
            for entry in party_entries:
                row: dict[str, Any] = {
                    "productCode": getattr(entry, "product_code", None),
                    "quantity": getattr(entry, "quantity"),
                    "rate": getattr(entry, "rate"),
                    "projectCode": getattr(entry, "project_code", None),
                }
                if getattr(entry, "gst_code", None):
                    row["gstCode"] = entry.gst_code
                if getattr(entry, "gst_rate", None) is not None:
                    row["gstRate"] = entry.gst_rate
                if getattr(entry, "adt_code", None):
                    row["adtCode"] = entry.adt_code
                if getattr(entry, "fed_code", None):
                    row["fedCode"] = entry.fed_code
                raw_lines.append(row)

            taxed = await self._tax.compute_sales_lines(
                company_id=company_id, raw_lines=raw_lines
            )
            repo_lines = [line.to_repo_dict() for line in taxed.lines]
            repo_lines = merge_line_description_fields(repo_lines, party_entries)

            invoice_number = str(
                await self._numbers.reserve_next(company_id=company_id, sequence_key="SI")
            )
            row = await self._sales_invoices.create_invoice(
                company_id=company_id,
                invoice_number=invoice_number,
                invoice_date=invoice_date,
                customer_id=customer_id,
                lines=repo_lines,
                journal_id=None,
                custom_fields=custom_fields or None,
            )
            if taxed.summaries and prisma is not None:
                await self._tax.persist_tax_summaries(
                    company_id=company_id,
                    document_kind="SI",
                    document_id=row.id,
                    summaries=taxed.summaries,
                    db=prisma,
                )
            created.append(
                {
                    "id": row.id,
                    "documentNumber": row.invoiceNumber,
                    "customerId": customer_id,
                    "totalAmount": str(row.totalAmount),
                }
            )

        return {"created": created, "count": len(created)}

    async def create_batch_supplier_bills(
        self,
        *,
        company_id: str,
        bill_date: datetime,
        entries: list[Any],
        smart_filters: dict[str, str] | None = None,
        prisma: Any | None = None,
    ) -> dict[str, Any]:
        if not entries:
            raise ValidationAppError("At least one batch row is required")

        await self._lock_date.assert_not_locked(
            company_id=company_id,
            document_date=bill_date,
            document_label="supplier bill",
        )

        grouped: dict[str, list[Any]] = defaultdict(list)
        for entry in entries:
            party_id = str(getattr(entry, "supplier_id", "") or "").strip()
            if not party_id:
                raise ValidationAppError("Each batch row requires a supplier")
            grouped[party_id].append(entry)

        custom_fields = smart_filters_custom_fields(smart_filters)
        created: list[dict[str, Any]] = []

        for supplier_id, party_entries in grouped.items():
            raw_lines: list[dict[str, Any]] = []
            for entry in party_entries:
                row: dict[str, Any] = {
                    "productCode": getattr(entry, "product_code", None),
                    "quantity": getattr(entry, "quantity"),
                    "rate": getattr(entry, "rate"),
                }
                if getattr(entry, "gst_code", None):
                    row["gstCode"] = entry.gst_code
                if getattr(entry, "gst_rate", None) is not None:
                    row["gstRate"] = entry.gst_rate
                if getattr(entry, "adt_code", None):
                    row["adtCode"] = entry.adt_code
                if getattr(entry, "fed_code", None):
                    row["fedCode"] = entry.fed_code
                raw_lines.append(row)

            taxed = await self._tax.compute_purchase_lines(
                company_id=company_id, raw_lines=raw_lines
            )
            repo_lines = [line.to_repo_dict() for line in taxed.lines]
            repo_lines = merge_line_description_fields(repo_lines, party_entries)

            bill_number = str(
                await self._numbers.reserve_next(company_id=company_id, sequence_key="VI")
            )
            row = await self._supplier_bills.create_bill(
                company_id=company_id,
                bill_number=bill_number,
                bill_date=bill_date,
                supplier_id=supplier_id,
                lines=repo_lines,
                journal_id=None,
                custom_fields=custom_fields or None,
            )
            if taxed.summaries and prisma is not None:
                await self._tax.persist_tax_summaries(
                    company_id=company_id,
                    document_kind="VI",
                    document_id=row.id,
                    summaries=taxed.summaries,
                    db=prisma,
                )
            created.append(
                {
                    "id": row.id,
                    "documentNumber": row.billNumber,
                    "supplierId": supplier_id,
                    "totalAmount": str(row.totalAmount),
                }
            )

        return {"created": created, "count": len(created)}
