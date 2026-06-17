"""Receipt / payment allocation against open invoices / bills — catalog §3.15.

Two modes:

- **Explicit**: the caller provides ``[(invoice_id, amount), ...]``; the service
  validates totals (per-invoice remaining + receipt cap) and writes
  ``SalesReceiptAllocation`` / ``SupplierPaymentAllocation`` rows.
- **Auto-FIFO**: walks the party's open invoices/bills oldest-first, consuming
  the unallocated portion of the receipt/payment until exhausted or no more
  open documents remain.

Per-invoice ``remaining = totalAmount - sum(existing allocations)``.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from prisma_generated import Prisma

from app.core.exceptions import ValidationAppError


@dataclass(frozen=True, slots=True)
class AllocationLine:
    """One explicit allocation row."""

    document_id: str
    amount: Decimal


@dataclass(frozen=True, slots=True)
class AllocationResult:
    """Outcome of an allocation operation."""

    allocations: list[dict]
    total_allocated: Decimal
    unallocated_balance: Decimal


class AllocationService:
    """FIFO + explicit allocation for sales receipts and supplier payments."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    # ------------------------------ Sales receipts ------------------------------

    async def allocate_sales_receipt(
        self,
        *,
        company_id: str,
        receipt_id: str,
        customer_id: str,
        receipt_total: Decimal,
        auto_fifo: bool,
        explicit: list[AllocationLine] | None,
    ) -> AllocationResult:
        if auto_fifo and explicit:
            raise ValidationAppError("Choose either auto-FIFO or explicit allocations, not both.")

        if explicit:
            await self._validate_explicit_sales(
                company_id=company_id,
                customer_id=customer_id,
                explicit=explicit,
                receipt_total=receipt_total,
            )
            rows = await self._write_sales_allocations(
                receipt_id=receipt_id, allocations=explicit
            )
            allocated = sum((a.amount for a in explicit), Decimal(0))
            return AllocationResult(
                allocations=rows,
                total_allocated=allocated,
                unallocated_balance=receipt_total - allocated,
            )

        if not auto_fifo:
            return AllocationResult(
                allocations=[],
                total_allocated=Decimal(0),
                unallocated_balance=receipt_total,
            )

        # Auto-FIFO: oldest open invoice first.
        open_invoices = await self._open_sales_invoices(
            company_id=company_id, customer_id=customer_id
        )
        plan = _build_fifo_plan(receipt_total, open_invoices)
        if not plan:
            return AllocationResult(
                allocations=[],
                total_allocated=Decimal(0),
                unallocated_balance=receipt_total,
            )
        rows = await self._write_sales_allocations(receipt_id=receipt_id, allocations=plan)
        allocated = sum((a.amount for a in plan), Decimal(0))
        return AllocationResult(
            allocations=rows,
            total_allocated=allocated,
            unallocated_balance=receipt_total - allocated,
        )

    async def list_open_sales_invoices(
        self,
        *,
        company_id: str,
        customer_id: str,
    ) -> list[dict]:
        """Open invoices with remaining balance for allocation UI."""

        open_rows = await self._open_sales_invoices(
            company_id=company_id, customer_id=customer_id
        )
        if not open_rows:
            return []
        ids = [row[0] for row in open_rows]
        invoices = await self._db.salesinvoice.find_many(
            where={"id": {"in": ids}},
            order={"invoiceDate": "asc"},
        )
        remaining_map = dict(open_rows)
        return [
            {
                "id": inv.id,
                "invoiceNumber": inv.invoiceNumber,
                "invoiceDate": inv.invoiceDate.isoformat(),
                "totalAmount": str(inv.totalAmount),
                "remaining": str(remaining_map[inv.id]),
            }
            for inv in invoices
            if inv.id in remaining_map
        ]

    async def list_open_supplier_bills(
        self,
        *,
        company_id: str,
        supplier_id: str,
    ) -> list[dict]:
        """Open bills with remaining balance for allocation UI."""

        open_rows = await self._open_supplier_bills(
            company_id=company_id, supplier_id=supplier_id
        )
        if not open_rows:
            return []
        ids = [row[0] for row in open_rows]
        bills = await self._db.supplierbill.find_many(
            where={"id": {"in": ids}},
            order={"billDate": "asc"},
        )
        remaining_map = dict(open_rows)
        return [
            {
                "id": bill.id,
                "billNumber": bill.billNumber,
                "billDate": bill.billDate.isoformat(),
                "totalAmount": str(bill.totalAmount),
                "remaining": str(remaining_map[bill.id]),
            }
            for bill in bills
            if bill.id in remaining_map
        ]

    async def _open_sales_invoices(
        self,
        *,
        company_id: str,
        customer_id: str,
    ) -> list[tuple[str, Decimal]]:
        invoices = await self._db.salesinvoice.find_many(
            where={
                "companyId": company_id,
                "customerId": customer_id,
                "remainingAmount": {"gt": 0},
            },
            order={"invoiceDate": "asc"},
            take=10_000,
        )
        return [(inv.id, inv.remainingAmount) for inv in invoices]

    async def _validate_explicit_sales(
        self,
        *,
        company_id: str,
        customer_id: str,
        explicit: list[AllocationLine],
        receipt_total: Decimal,
    ) -> None:
        total = sum((a.amount for a in explicit), Decimal(0))
        if total <= 0:
            raise ValidationAppError("Allocation total must be positive.")
        if total > receipt_total:
            raise ValidationAppError(
                f"Allocation total {total} exceeds receipt total {receipt_total}."
            )
        invoice_ids = [a.document_id for a in explicit]
        invoices = await self._db.salesinvoice.find_many(
            where={"id": {"in": invoice_ids}},
            include={"allocations": True},
        )
        lookup = {i.id: i for i in invoices}
        for line in explicit:
            inv = lookup.get(line.document_id)
            if inv is None:
                raise ValidationAppError(f"Invoice {line.document_id} not found.")
            if inv.companyId != company_id or inv.customerId != customer_id:
                raise ValidationAppError(
                    f"Invoice {line.document_id} does not belong to this customer."
                )
            existing = sum((a.amount for a in (inv.allocations or [])), Decimal(0))
            remaining = inv.totalAmount - existing
            if line.amount <= 0:
                raise ValidationAppError("Allocation amount must be positive.")
            if line.amount > remaining:
                raise ValidationAppError(
                    f"Allocation {line.amount} exceeds remaining {remaining} on invoice."
                )

    async def _write_sales_allocations(
        self,
        *,
        receipt_id: str,
        allocations: list[AllocationLine],
    ) -> list[dict]:
        from app.services.subledger_remaining_service import SubledgerRemainingService

        out: list[dict] = []
        invoice_ids: list[str] = []
        for line in allocations:
            row = await self._db.salesreceiptallocation.create(
                data={
                    "salesReceiptId": receipt_id,
                    "salesInvoiceId": line.document_id,
                    "amount": line.amount,
                }
            )
            invoice_ids.append(line.document_id)
            out.append(
                {
                    "id": row.id,
                    "salesInvoiceId": row.salesInvoiceId,
                    "amount": str(row.amount),
                }
            )
        await SubledgerRemainingService(self._db).sync_sales_invoices(
            invoice_ids=invoice_ids
        )
        return out

    # ----------------------------- Supplier payments ----------------------------

    async def allocate_supplier_payment(
        self,
        *,
        company_id: str,
        payment_id: str,
        supplier_id: str,
        payment_total: Decimal,
        auto_fifo: bool,
        explicit: list[AllocationLine] | None,
    ) -> AllocationResult:
        if auto_fifo and explicit:
            raise ValidationAppError("Choose either auto-FIFO or explicit allocations, not both.")

        if explicit:
            await self._validate_explicit_purchases(
                company_id=company_id,
                supplier_id=supplier_id,
                explicit=explicit,
                payment_total=payment_total,
            )
            rows = await self._write_purchase_allocations(
                payment_id=payment_id, allocations=explicit
            )
            allocated = sum((a.amount for a in explicit), Decimal(0))
            return AllocationResult(
                allocations=rows,
                total_allocated=allocated,
                unallocated_balance=payment_total - allocated,
            )

        if not auto_fifo:
            return AllocationResult(
                allocations=[],
                total_allocated=Decimal(0),
                unallocated_balance=payment_total,
            )

        open_bills = await self._open_supplier_bills(
            company_id=company_id, supplier_id=supplier_id
        )
        plan = _build_fifo_plan(payment_total, open_bills)
        if not plan:
            return AllocationResult(
                allocations=[],
                total_allocated=Decimal(0),
                unallocated_balance=payment_total,
            )
        rows = await self._write_purchase_allocations(payment_id=payment_id, allocations=plan)
        allocated = sum((a.amount for a in plan), Decimal(0))
        return AllocationResult(
            allocations=rows,
            total_allocated=allocated,
            unallocated_balance=payment_total - allocated,
        )

    async def _open_supplier_bills(
        self,
        *,
        company_id: str,
        supplier_id: str,
    ) -> list[tuple[str, Decimal]]:
        bills = await self._db.supplierbill.find_many(
            where={
                "companyId": company_id,
                "supplierId": supplier_id,
                "remainingAmount": {"gt": 0},
            },
            order={"billDate": "asc"},
            take=10_000,
        )
        return [(bill.id, bill.remainingAmount) for bill in bills]

    async def _validate_explicit_purchases(
        self,
        *,
        company_id: str,
        supplier_id: str,
        explicit: list[AllocationLine],
        payment_total: Decimal,
    ) -> None:
        total = sum((a.amount for a in explicit), Decimal(0))
        if total <= 0:
            raise ValidationAppError("Allocation total must be positive.")
        if total > payment_total:
            raise ValidationAppError(
                f"Allocation total {total} exceeds payment total {payment_total}."
            )
        bill_ids = [a.document_id for a in explicit]
        bills = await self._db.supplierbill.find_many(
            where={"id": {"in": bill_ids}},
            include={"allocations": True},
        )
        lookup = {b.id: b for b in bills}
        for line in explicit:
            bill = lookup.get(line.document_id)
            if bill is None:
                raise ValidationAppError(f"Bill {line.document_id} not found.")
            if bill.companyId != company_id or bill.supplierId != supplier_id:
                raise ValidationAppError(
                    f"Bill {line.document_id} does not belong to this supplier."
                )
            existing = sum((a.amount for a in (bill.allocations or [])), Decimal(0))
            remaining = bill.totalAmount - existing
            if line.amount <= 0:
                raise ValidationAppError("Allocation amount must be positive.")
            if line.amount > remaining:
                raise ValidationAppError(
                    f"Allocation {line.amount} exceeds remaining {remaining} on bill."
                )

    async def _write_purchase_allocations(
        self,
        *,
        payment_id: str,
        allocations: list[AllocationLine],
    ) -> list[dict]:
        from app.services.subledger_remaining_service import SubledgerRemainingService

        out: list[dict] = []
        bill_ids: list[str] = []
        for line in allocations:
            row = await self._db.supplierpaymentallocation.create(
                data={
                    "supplierPaymentId": payment_id,
                    "supplierBillId": line.document_id,
                    "amount": line.amount,
                }
            )
            bill_ids.append(line.document_id)
            out.append(
                {
                    "id": row.id,
                    "supplierBillId": row.supplierBillId,
                    "amount": str(row.amount),
                }
            )
        await SubledgerRemainingService(self._db).sync_supplier_bills(bill_ids=bill_ids)
        return out


def _build_fifo_plan(
    available: Decimal,
    open_docs: list[tuple[str, Decimal]],
) -> list[AllocationLine]:
    """Greedy fill oldest documents first up to ``available``."""

    plan: list[AllocationLine] = []
    remaining = available
    for doc_id, doc_remaining in open_docs:
        if remaining <= 0:
            break
        chunk = min(doc_remaining, remaining)
        plan.append(AllocationLine(document_id=doc_id, amount=chunk))
        remaining -= chunk
    return plan
