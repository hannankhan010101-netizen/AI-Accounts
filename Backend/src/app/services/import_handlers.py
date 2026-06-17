"""Bulk import row processors — P2."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from prisma_generated import Prisma

from app.repositories.journal_repository import JournalRepository
from app.repositories.sales_invoice_repository import SalesInvoiceRepository
from app.repositories.sales_receipt_repository import SalesReceiptRepository
from app.repositories.supplier_bill_repository import SupplierBillRepository
from app.repositories.supplier_payment_repository import SupplierPaymentRepository


class ImportHandlerResult:
    def __init__(
        self,
        *,
        created: int = 0,
        posted: int = 0,
        skipped: int = 0,
        errors: list[str] | None = None,
    ) -> None:
        self.created = created
        self.posted = posted
        self.skipped = skipped
        self.errors = errors or []


def _import_post_gl_enabled(options: dict[str, Any]) -> bool:
    return bool(options.get("postGl") or options.get("post_gl"))


def _group_wants_post(
    indexed_rows: list[tuple[int, dict[str, Any]]],
    *,
    options: dict[str, Any],
) -> bool:
    if _import_post_gl_enabled(options):
        return True
    return any(_str(row.get("status")).lower() == "posted" for _, row in indexed_rows)


def _row_wants_post(row: dict[str, Any], *, options: dict[str, Any]) -> bool:
    if _import_post_gl_enabled(options):
        return True
    return _str(row.get("status")).lower() == "posted"


async def process_import_job(
    *,
    db: Prisma,
    company_id: str,
    job_type: str,
    rows: list[dict[str, Any]],
    options: dict[str, Any] | None = None,
) -> ImportHandlerResult:
    """Dispatch by ``job_type`` string."""

    opts = options or {}
    handlers = {
        "customers": _import_customers,
        "products": _import_products,
        "bank_payments": _import_bank_payments,
        "bank_receipts": _import_bank_receipts,
        "roles": _import_roles,
        "journals": _import_journals,
        "suppliers": _import_suppliers,
        "supplier_bills": _import_supplier_bills,
        "sales_invoices": _import_sales_invoices,
        "sales_receipts": _import_sales_receipts,
        "supplier_payments": _import_supplier_payments,
        "opening_stock": _import_opening_stock,
        "product_tax_update": _import_product_tax_update,
    }
    handler = handlers.get(job_type)
    if handler is None:
        return ImportHandlerResult(
            skipped=len(rows),
            errors=[f"Unsupported jobType: {job_type}"],
        )
    if job_type == "roles":
        return await handler(
            db=db,
            company_id=company_id,
            rows=rows,
            skip_existing=bool(opts.get("skipExisting", True)),
        )
    return await handler(db=db, company_id=company_id, rows=rows, options=opts)


async def _import_roles(
    *,
    db: Prisma,
    company_id: str,
    rows: list[dict[str, Any]],
    skip_existing: bool = True,
    options: dict[str, Any] | None = None,
) -> ImportHandlerResult:
    """Bulk role create from queued import — P33."""

    from app.repositories.role_repository import RoleRepository

    repo = RoleRepository(db)
    result = ImportHandlerResult()
    for i, row in enumerate(rows, start=1):
        name = str(row.get("name", "")).strip()
        if not name:
            result.errors.append(f"Row {i}: name required")
            result.skipped += 1
            continue
        if name == "Administrator":
            result.errors.append(f"Row {i}: reserved name Administrator")
            result.skipped += 1
            continue
        perms_raw = row.get("permissions", [])
        permissions = (
            [str(p) for p in perms_raw] if isinstance(perms_raw, list) else []
        )
        existing = await db.role.find_first(
            where={"companyId": company_id, "name": name},
        )
        if existing is not None:
            if skip_existing:
                result.skipped += 1
                continue
            result.errors.append(f"Row {i}: role name already exists")
            result.skipped += 1
            continue
        try:
            await repo.create_role(
                company_id=company_id,
                name=name,
                permissions=permissions,
            )
            result.created += 1
        except ValueError as exc:
            result.errors.append(f"Row {i}: {exc}")
            result.skipped += 1
    return result


async def _import_suppliers(
    *,
    db: Prisma,
    company_id: str,
    rows: list[dict[str, Any]],
    options: dict[str, Any] | None = None,
) -> ImportHandlerResult:
    return await _import_master_codes(
        db=db,
        company_id=company_id,
        rows=rows,
        model=db.supplier,
        code_keys=("code", "supplierCode"),
        name_keys=("name", "supplierName"),
    )


async def _import_customers(
    *,
    db: Prisma,
    company_id: str,
    rows: list[dict[str, Any]],
    options: dict[str, Any] | None = None,
) -> ImportHandlerResult:
    return await _import_master_codes(
        db=db,
        company_id=company_id,
        rows=rows,
        model=db.customer,
        code_keys=("code", "customerCode"),
        name_keys=("name", "customerName"),
    )


async def _import_products(
    *,
    db: Prisma,
    company_id: str,
    rows: list[dict[str, Any]],
    options: dict[str, Any] | None = None,
) -> ImportHandlerResult:
    result = ImportHandlerResult()
    pending: list[dict[str, Any]] = []
    codes: list[str] = []
    for i, row in enumerate(rows, start=1):
        code = _str(row.get("code") or row.get("productCode"))
        name = _str(row.get("name") or row.get("productName"))
        if not code or not name:
            result.errors.append(f"Row {i}: code and name required")
            result.skipped += 1
            continue
        codes.append(code)
        pending.append(
            {
                "row": i,
                "data": {
                    "companyId": company_id,
                    "code": code,
                    "name": name,
                    "cost": _dec(row.get("cost") or row.get("unitCost") or 0),
                    "isStock": _bool(row.get("isStock", True)),
                },
            }
        )
    if not pending:
        return result
    existing_rows = await db.product.find_many(
        where={"companyId": company_id, "code": {"in": list(dict.fromkeys(codes))}},
    )
    existing_codes = {p.code for p in existing_rows}
    batch: list[dict[str, Any]] = []
    for item in pending:
        if item["data"]["code"] in existing_codes:
            result.skipped += 1
            continue
        batch.append(item["data"])
    for chunk_start in range(0, len(batch), 500):
        chunk = batch[chunk_start : chunk_start + 500]
        if chunk:
            await db.product.create_many(data=chunk)
            result.created += len(chunk)
    return result


async def _import_master_codes(
    *,
    db: Prisma,
    company_id: str,
    rows: list[dict[str, Any]],
    model: Any,
    code_keys: tuple[str, ...],
    name_keys: tuple[str, ...],
) -> ImportHandlerResult:
    result = ImportHandlerResult()
    pending: list[dict[str, Any]] = []
    codes: list[str] = []
    for i, row in enumerate(rows, start=1):
        code = ""
        for key in code_keys:
            code = _str(row.get(key))
            if code:
                break
        name = ""
        for key in name_keys:
            name = _str(row.get(key))
            if name:
                break
        if not code or not name:
            result.errors.append(f"Row {i}: code and name required")
            result.skipped += 1
            continue
        codes.append(code)
        pending.append(
            {"data": {"companyId": company_id, "code": code, "name": name}}
        )
    if not pending:
        return result
    existing_rows = await model.find_many(
        where={"companyId": company_id, "code": {"in": list(dict.fromkeys(codes))}},
    )
    existing_codes = {r.code for r in existing_rows}
    batch = [p["data"] for p in pending if p["data"]["code"] not in existing_codes]
    result.skipped += len(pending) - len(batch)
    for chunk_start in range(0, len(batch), 500):
        chunk = batch[chunk_start : chunk_start + 500]
        if chunk:
            await model.create_many(data=chunk)
            result.created += len(chunk)
    return result


OPENING_STOCK_BATCH_DEFAULT = "OPENING"


async def _import_opening_stock(
    *,
    db: Prisma,
    company_id: str,
    rows: list[dict[str, Any]],
    options: dict[str, Any] | None = None,
) -> ImportHandlerResult:
    """Upsert product batch quantities for opening stock — FA §7 / migrate_supplemental parity."""

    from datetime import datetime

    result = ImportHandlerResult()
    products = await db.product.find_many(where={"companyId": company_id})
    product_codes = {p.code for p in products}

    for i, row in enumerate(rows, start=1):
        code = _str(row.get("productCode") or row.get("code") or row.get("Code"))
        qty = _dec(row.get("quantity") or row.get("quantityOnHand") or row.get("Quantity"))
        if not code:
            result.errors.append(f"Row {i}: productCode required")
            result.skipped += 1
            continue
        if code not in product_codes:
            result.errors.append(f"Row {i}: unknown product {code}")
            result.skipped += 1
            continue
        if qty <= 0:
            result.errors.append(f"Row {i}: quantity must be positive")
            result.skipped += 1
            continue

        batch_number = (
            _str(row.get("batchNumber") or row.get("batch") or row.get("Batch"))
            or OPENING_STOCK_BATCH_DEFAULT
        )
        expiry_raw = row.get("expiryDate") or row.get("expiry")
        expiry: datetime | None = None
        if expiry_raw:
            if isinstance(expiry_raw, str):
                expiry = datetime.fromisoformat(expiry_raw.replace("Z", "+00:00"))
            elif isinstance(expiry_raw, datetime):
                expiry = expiry_raw

        notes = _str(row.get("notes")) or "Opening stock import"
        existing = await db.productbatch.find_first(
            where={
                "companyId": company_id,
                "productCode": code,
                "batchNumber": batch_number,
            }
        )
        data = {
            "quantityOnHand": qty,
            "expiryDate": expiry,
            "notes": notes,
        }
        if existing:
            await db.productbatch.update(where={"id": existing.id}, data=data)
        else:
            await db.productbatch.create(
                data={
                    "companyId": company_id,
                    "productCode": code,
                    "batchNumber": batch_number,
                    **data,
                }
            )
        result.created += 1

    return result


async def _import_product_tax_update(
    *,
    db: Prisma,
    company_id: str,
    rows: list[dict[str, Any]],
    options: dict[str, Any] | None = None,
) -> ImportHandlerResult:
    """Bulk-update product tax codes in customFields — FA §7 bulk tax update."""

    _ = options
    result = ImportHandlerResult()
    tax_keys = ("gstCode", "fedCode", "adtCode", "whtCode")

    for i, row in enumerate(rows, start=1):
        code = _str(row.get("productCode") or row.get("code") or row.get("Code"))
        if not code:
            result.errors.append(f"Row {i}: productCode required")
            result.skipped += 1
            continue
        product = await db.product.find_first(
            where={"companyId": company_id, "code": code}
        )
        if product is None:
            result.errors.append(f"Row {i}: unknown product {code}")
            result.skipped += 1
            continue

        patch: dict[str, str] = {}
        for key in tax_keys:
            val = _str(row.get(key) or row.get(key.upper()))
            if val:
                patch[key] = val
        if not patch:
            result.errors.append(f"Row {i}: at least one tax code required")
            result.skipped += 1
            continue

        existing = product.customFields if isinstance(product.customFields, dict) else {}
        merged = {**existing, **patch}
        await db.product.update(
            where={"id": product.id},
            data={"customFields": merged},
        )
        result.created += 1

    return result


async def _import_bank_payments(
    *,
    db: Prisma,
    company_id: str,
    rows: list[dict[str, Any]],
    options: dict[str, Any] | None = None,
) -> ImportHandlerResult:
    """Create bank payment shells — GL posting requires nominal + bank setup separately."""

    from datetime import datetime

    result = ImportHandlerResult()
    for i, row in enumerate(rows, start=1):
        bank_code = _str(row.get("bankAccountId") or row.get("bankCode"))
        amount = _dec(row.get("amount") or row.get("totalAmount"))
        nominal = _str(row.get("nominalCode"))
        if not bank_code or amount <= 0 or not nominal:
            result.errors.append(f"Row {i}: bankAccountId, amount, nominalCode required")
            result.skipped += 1
            continue
        bank = await db.bankaccount.find_first(
            where={"companyId": company_id, "id": bank_code}
        )
        if bank is None:
            bank = await db.bankaccount.find_first(
                where={"companyId": company_id, "nominalCode": bank_code}
            )
        if bank is None:
            result.errors.append(f"Row {i}: bank account not found")
            result.skipped += 1
            continue
        pay_date = row.get("paymentDate") or row.get("date")
        if isinstance(pay_date, str):
            pay_date = datetime.fromisoformat(pay_date.replace("Z", "+00:00"))
        elif not isinstance(pay_date, datetime):
            pay_date = datetime.utcnow()
        seq = await db.documentnumbersequence.find_unique(
            where={"companyId_key": {"companyId": company_id, "key": "EP"}}
        )
        next_no = (seq.nextValue if seq else 1)
        if seq:
            await db.documentnumbersequence.update(
                where={"companyId_key": {"companyId": company_id, "key": "EP"}},
                data={"nextValue": next_no + 1},
            )
        await db.bankpayment.create(
            data={
                "companyId": company_id,
                "voucherNumber": str(next_no),
                "paymentDate": pay_date,
                "bankAccountId": bank.id,
                "nominalCode": nominal,
                "totalAmount": amount,
                "status": "posted",
            }
        )
        result.created += 1
    return result


async def _import_bank_receipts(
    *,
    db: Prisma,
    company_id: str,
    rows: list[dict[str, Any]],
    options: dict[str, Any] | None = None,
) -> ImportHandlerResult:
    """Create bank receipt shells (IR) — GL posting requires nominal + bank setup."""

    from datetime import datetime

    result = ImportHandlerResult()
    for i, row in enumerate(rows, start=1):
        bank_code = _str(row.get("bankAccountId") or row.get("bankCode"))
        amount = _dec(row.get("amount") or row.get("totalAmount"))
        nominal = _str(row.get("nominalCode"))
        if not bank_code or amount <= 0 or not nominal:
            result.errors.append(f"Row {i}: bankAccountId, amount, nominalCode required")
            result.skipped += 1
            continue
        bank = await db.bankaccount.find_first(
            where={"companyId": company_id, "id": bank_code}
        )
        if bank is None:
            bank = await db.bankaccount.find_first(
                where={"companyId": company_id, "nominalCode": bank_code}
            )
        if bank is None:
            result.errors.append(f"Row {i}: bank account not found")
            result.skipped += 1
            continue
        receipt_date = row.get("receiptDate") or row.get("date")
        if isinstance(receipt_date, str):
            receipt_date = datetime.fromisoformat(receipt_date.replace("Z", "+00:00"))
        elif not isinstance(receipt_date, datetime):
            receipt_date = datetime.utcnow()
        seq = await db.documentnumbersequence.find_unique(
            where={"companyId_key": {"companyId": company_id, "key": "IR"}}
        )
        next_no = seq.nextValue if seq else 1
        if seq:
            await db.documentnumbersequence.update(
                where={"companyId_key": {"companyId": company_id, "key": "IR"}},
                data={"nextValue": next_no + 1},
            )
        await db.bankreceipt.create(
            data={
                "companyId": company_id,
                "voucherNumber": str(next_no),
                "receiptDate": receipt_date,
                "bankAccountId": bank.id,
                "nominalCode": nominal,
                "totalAmount": amount,
                "status": "posted",
            }
        )
        result.created += 1
    return result


def _str(v: Any) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    return s or None


def _dec(v: Any) -> Decimal:
    try:
        return Decimal(str(v))
    except (InvalidOperation, TypeError):
        return Decimal(0)


def _bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    return str(v).lower() in {"1", "true", "yes", "y"}


async def _import_sales_invoices(
    *,
    db: Prisma,
    company_id: str,
    rows: list[dict[str, Any]],
    options: dict[str, Any] | None = None,
) -> ImportHandlerResult:
    """Import sales invoices grouped by ``invoiceRef``; optional GL post."""

    opts = options or {}
    grouped: dict[str, list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    for i, row in enumerate(rows, start=1):
        key = _str(row.get("invoiceRef") or row.get("invoiceNumber") or row.get("refNo"))
        if not key:
            key = f"__row_{i}"
        grouped[key].append((i, row))

    repo = SalesInvoiceRepository(db)
    result = ImportHandlerResult()
    engine = None

    for _key, indexed_rows in grouped.items():
        lines: list[dict[str, Any]] = []
        invoice_date: datetime | None = None
        customer_id: str | None = None
        row_nums: list[int] = []

        for row_num, row in indexed_rows:
            row_nums.append(row_num)
            code = _str(row.get("customerCode") or row.get("customerId"))
            if customer_id is None and code:
                customer = await db.customer.find_first(
                    where={"companyId": company_id, "code": code}
                )
                if customer is None:
                    result.errors.append(f"Row {row_num}: customer {code} not found")
                    customer_id = ""
                    break
                customer_id = customer.id

            qty = _dec(row.get("quantity") or 1)
            rate = _dec(row.get("rate") or row.get("amount") or 0)
            if rate <= 0:
                result.errors.append(f"Row {row_num}: rate required")
                continue
            subtotal = _quantize_line(qty * rate)
            lines.append(
                {
                    "productCode": _str(row.get("productCode")),
                    "quantity": qty,
                    "rate": rate,
                    "lineSubtotal": subtotal,
                    "gstRate": Decimal(0),
                    "taxAmount": Decimal(0),
                    "lineTotal": subtotal,
                }
            )
            raw_date = row.get("invoiceDate") or row.get("date")
            if invoice_date is None and raw_date:
                if isinstance(raw_date, str):
                    invoice_date = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
                elif isinstance(raw_date, datetime):
                    invoice_date = raw_date

        if not customer_id or customer_id == "":
            result.skipped += len(indexed_rows)
            continue
        if not lines:
            result.skipped += len(indexed_rows)
            continue
        if invoice_date is None:
            invoice_date = datetime.utcnow()

        seq = await db.documentnumbersequence.find_unique(
            where={"companyId_key": {"companyId": company_id, "key": "SI"}}
        )
        next_no = seq.nextValue if seq else 1
        if seq:
            await db.documentnumbersequence.update(
                where={"companyId_key": {"companyId": company_id, "key": "SI"}},
                data={"nextValue": next_no + 1},
            )

        try:
            invoice = await repo.create_invoice(
                company_id=company_id,
                invoice_number=str(next_no),
                invoice_date=invoice_date,
                customer_id=customer_id,
                lines=lines,
            )
            result.created += 1
            if _group_wants_post(indexed_rows, options=opts):
                if engine is None:
                    from app.services.import_posting_context import (
                        build_import_posting_stack,
                    )

                    engine, _ = build_import_posting_stack(db)
                try:
                    await engine.approve_sales_invoice(
                        company_id=company_id, invoice_id=invoice.id
                    )
                    result.posted += 1
                except Exception as post_exc:  # noqa: BLE001
                    result.errors.append(f"Invoice {_key} GL post: {post_exc}")
        except Exception as exc:  # noqa: BLE001
            result.errors.append(f"Invoice {_key} (rows {row_nums}): {exc}")
            result.skipped += len(indexed_rows)

    return result


async def _import_sales_receipts(
    *,
    db: Prisma,
    company_id: str,
    rows: list[dict[str, Any]],
    options: dict[str, Any] | None = None,
) -> ImportHandlerResult:
    """Import sales receipts; optional GL post (one row per receipt)."""

    opts = options or {}

    repo = SalesReceiptRepository(db)
    result = ImportHandlerResult()
    posting_service = None
    default_bank = await db.bankaccount.find_first(
        where={"companyId": company_id},
        order={"name": "asc"},
    )
    if default_bank is None:
        return ImportHandlerResult(
            skipped=len(rows),
            errors=["No bank account — create a bank account first"],
        )

    for i, row in enumerate(rows, start=1):
        code = _str(row.get("customerCode") or row.get("customerId"))
        amount = _dec(row.get("totalAmount") or row.get("amount") or 0)
        if not code or amount <= 0:
            result.errors.append(f"Row {i}: customerCode and totalAmount required")
            result.skipped += 1
            continue

        customer = await db.customer.find_first(
            where={"companyId": company_id, "code": code}
        )
        if customer is None:
            result.errors.append(f"Row {i}: customer {code} not found")
            result.skipped += 1
            continue

        bank = default_bank
        bank_key = _str(row.get("bankAccountId") or row.get("bankCode"))
        if bank_key:
            found = await db.bankaccount.find_first(
                where={"companyId": company_id, "id": bank_key}
            )
            if found is None:
                found = await db.bankaccount.find_first(
                    where={"companyId": company_id, "nominalCode": bank_key}
                )
            if found is not None:
                bank = found

        receipt_date = row.get("receiptDate") or row.get("date")
        if isinstance(receipt_date, str):
            receipt_date = datetime.fromisoformat(receipt_date.replace("Z", "+00:00"))
        elif not isinstance(receipt_date, datetime):
            receipt_date = datetime.utcnow()

        seq = await db.documentnumbersequence.find_unique(
            where={"companyId_key": {"companyId": company_id, "key": "SR"}}
        )
        next_no = seq.nextValue if seq else 1
        if seq:
            await db.documentnumbersequence.update(
                where={"companyId_key": {"companyId": company_id, "key": "SR"}},
                data={"nextValue": next_no + 1},
            )

        try:
            receipt = await repo.create_receipt(
                company_id=company_id,
                receipt_number=str(next_no),
                receipt_date=receipt_date,
                customer_id=customer.id,
                bank_account_id=bank.id,
                total_amount=amount,
                journal_id=None,
                status="draft",
            )
            result.created += 1
            if _row_wants_post(row, options=opts):
                if posting_service is None:
                    from app.services.import_posting_context import (
                        build_import_posting_stack,
                    )

                    _, posting_service = build_import_posting_stack(db)
                journal = await posting_service.post_sales_receipt(
                    company_id=company_id,
                    receipt_date=receipt_date,
                    receipt_number=str(next_no),
                    bank_account_id=bank.id,
                    total_amount=amount,
                )
                if journal is None:
                    result.errors.append(
                        f"Row {i}: GL post failed — check receivables/bank nominals"
                    )
                else:
                    await repo.link_receipt_journal(
                        receipt_id=receipt.id, journal_id=journal.id
                    )
                    result.posted += 1
        except Exception as exc:  # noqa: BLE001
            result.errors.append(f"Row {i}: {exc}")
            result.skipped += 1

    return result


async def _import_supplier_payments(
    *,
    db: Prisma,
    company_id: str,
    rows: list[dict[str, Any]],
    options: dict[str, Any] | None = None,
) -> ImportHandlerResult:
    """Import supplier payments; optional GL post (one row per payment)."""

    opts = options or {}

    repo = SupplierPaymentRepository(db)
    result = ImportHandlerResult()
    posting_service = None
    default_bank = await db.bankaccount.find_first(
        where={"companyId": company_id},
        order={"name": "asc"},
    )
    if default_bank is None:
        return ImportHandlerResult(
            skipped=len(rows),
            errors=["No bank account — create a bank account first"],
        )

    for i, row in enumerate(rows, start=1):
        code = _str(row.get("supplierCode") or row.get("supplierId"))
        amount = _dec(row.get("totalAmount") or row.get("amount") or 0)
        if not code or amount <= 0:
            result.errors.append(f"Row {i}: supplierCode and totalAmount required")
            result.skipped += 1
            continue

        supplier = await db.supplier.find_first(
            where={"companyId": company_id, "code": code}
        )
        if supplier is None:
            result.errors.append(f"Row {i}: supplier {code} not found")
            result.skipped += 1
            continue

        bank = default_bank
        bank_key = _str(row.get("bankAccountId") or row.get("bankCode"))
        if bank_key:
            found = await db.bankaccount.find_first(
                where={"companyId": company_id, "id": bank_key}
            )
            if found is None:
                found = await db.bankaccount.find_first(
                    where={"companyId": company_id, "nominalCode": bank_key}
                )
            if found is not None:
                bank = found

        payment_date = row.get("paymentDate") or row.get("date")
        if isinstance(payment_date, str):
            payment_date = datetime.fromisoformat(payment_date.replace("Z", "+00:00"))
        elif not isinstance(payment_date, datetime):
            payment_date = datetime.utcnow()

        seq = await db.documentnumbersequence.find_unique(
            where={"companyId_key": {"companyId": company_id, "key": "VP"}}
        )
        next_no = seq.nextValue if seq else 1
        if seq:
            await db.documentnumbersequence.update(
                where={"companyId_key": {"companyId": company_id, "key": "VP"}},
                data={"nextValue": next_no + 1},
            )

        try:
            payment = await repo.create_payment(
                company_id=company_id,
                voucher_number=str(next_no),
                payment_date=payment_date,
                supplier_id=supplier.id,
                bank_account_id=bank.id,
                total_amount=amount,
                journal_id=None,
                status="draft",
            )
            result.created += 1
            if _row_wants_post(row, options=opts):
                if posting_service is None:
                    from app.services.import_posting_context import (
                        build_import_posting_stack,
                    )

                    _, posting_service = build_import_posting_stack(db)
                journal = await posting_service.post_supplier_payment(
                    company_id=company_id,
                    payment_date=payment_date,
                    voucher_number=str(next_no),
                    bank_account_id=bank.id,
                    total_amount=amount,
                )
                if journal is None:
                    result.errors.append(
                        f"Row {i}: GL post failed — check payables/bank nominals"
                    )
                else:
                    await repo.link_payment_journal(
                        payment_id=payment.id, journal_id=journal.id
                    )
                    result.posted += 1
        except Exception as exc:  # noqa: BLE001
            result.errors.append(f"Row {i}: {exc}")
            result.skipped += 1

    return result


async def _import_supplier_bills(
    *,
    db: Prisma,
    company_id: str,
    rows: list[dict[str, Any]],
    options: dict[str, Any] | None = None,
) -> ImportHandlerResult:
    """Import supplier bills grouped by ``billRef``; optional GL post."""

    grouped: dict[str, list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    for i, row in enumerate(rows, start=1):
        key = _str(row.get("billRef") or row.get("billNumber") or row.get("refNo"))
        if not key:
            key = f"__row_{i}"
        grouped[key].append((i, row))

    opts = options or {}
    repo = SupplierBillRepository(db)
    result = ImportHandlerResult()
    engine = None

    for _key, indexed_rows in grouped.items():
        lines: list[dict[str, Any]] = []
        bill_date: datetime | None = None
        supplier_id: str | None = None
        row_nums: list[int] = []

        for row_num, row in indexed_rows:
            row_nums.append(row_num)
            code = _str(row.get("supplierCode") or row.get("supplierId"))
            if supplier_id is None and code:
                supplier = await db.supplier.find_first(
                    where={"companyId": company_id, "code": code}
                )
                if supplier is None:
                    result.errors.append(f"Row {row_num}: supplier {code} not found")
                    supplier_id = ""
                    break
                supplier_id = supplier.id

            qty = _dec(row.get("quantity") or 1)
            rate = _dec(row.get("rate") or row.get("amount") or 0)
            if rate <= 0:
                result.errors.append(f"Row {row_num}: rate required")
                continue
            subtotal = _quantize_line(qty * rate)
            lines.append(
                {
                    "productCode": _str(row.get("productCode")),
                    "quantity": qty,
                    "rate": rate,
                    "lineSubtotal": subtotal,
                    "gstRate": Decimal(0),
                    "taxAmount": Decimal(0),
                    "lineTotal": subtotal,
                }
            )
            raw_date = row.get("billDate") or row.get("date")
            if bill_date is None and raw_date:
                if isinstance(raw_date, str):
                    bill_date = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
                elif isinstance(raw_date, datetime):
                    bill_date = raw_date

        if not supplier_id or supplier_id == "":
            result.skipped += len(indexed_rows)
            continue
        if not lines:
            result.skipped += len(indexed_rows)
            continue
        if bill_date is None:
            bill_date = datetime.utcnow()

        seq = await db.documentnumbersequence.find_unique(
            where={"companyId_key": {"companyId": company_id, "key": "VI"}}
        )
        next_no = seq.nextValue if seq else 1
        if seq:
            await db.documentnumbersequence.update(
                where={"companyId_key": {"companyId": company_id, "key": "VI"}},
                data={"nextValue": next_no + 1},
            )

        try:
            bill = await repo.create_bill(
                company_id=company_id,
                bill_number=str(next_no),
                bill_date=bill_date,
                supplier_id=supplier_id,
                lines=lines,
            )
            result.created += 1
            if _group_wants_post(indexed_rows, options=opts):
                if engine is None:
                    from app.services.import_posting_context import (
                        build_import_posting_stack,
                    )

                    engine, _ = build_import_posting_stack(db)
                try:
                    await engine.approve_supplier_bill(
                        company_id=company_id, bill_id=bill.id
                    )
                    result.posted += 1
                except Exception as post_exc:  # noqa: BLE001
                    result.errors.append(f"Bill {_key} GL post: {post_exc}")
        except Exception as exc:  # noqa: BLE001
            result.errors.append(f"Bill {_key} (rows {row_nums}): {exc}")
            result.skipped += len(indexed_rows)

    return result


def _quantize_line(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.0001"))


async def _import_journals(
    *,
    db: Prisma,
    company_id: str,
    rows: list[dict[str, Any]],
    options: dict[str, Any] | None = None,
) -> ImportHandlerResult:
    """Import manual journals grouped by ``journalRef`` (or ``refNo``)."""

    grouped: dict[str, list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    for i, row in enumerate(rows, start=1):
        key = _str(row.get("journalRef") or row.get("refNo") or row.get("reference"))
        if not key:
            key = f"__row_{i}"
        grouped[key].append((i, row))

    repo = JournalRepository(db)
    result = ImportHandlerResult()

    for _key, indexed_rows in grouped.items():
        lines: list[dict[str, Any]] = []
        journal_date: datetime | None = None
        ref_no: str | None = None
        status = "draft"
        row_nums: list[int] = []

        for row_num, row in indexed_rows:
            row_nums.append(row_num)
            code = _str(row.get("nominalCode") or row.get("nominal"))
            debit = _dec(row.get("debit") or 0)
            credit = _dec(row.get("credit") or 0)
            if not code or (debit <= 0 and credit <= 0):
                result.errors.append(
                    f"Row {row_num}: nominalCode and debit or credit required"
                )
                continue
            if debit > 0 and credit > 0:
                result.errors.append(f"Row {row_num}: use debit or credit, not both")
                continue
            lines.append(
                {
                    "nominalCode": code,
                    "debit": debit,
                    "credit": credit,
                    "projectCode": _str(row.get("projectCode")),
                }
            )
            raw_date = row.get("journalDate") or row.get("date")
            if journal_date is None and raw_date:
                if isinstance(raw_date, str):
                    journal_date = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
                elif isinstance(raw_date, datetime):
                    journal_date = raw_date
            if ref_no is None:
                ref_no = _str(row.get("refNo") or row.get("reference"))
            raw_status = _str(row.get("status"))
            if raw_status and raw_status.lower() in {"posted", "draft"}:
                status = raw_status.lower()

        if not lines:
            result.skipped += len(indexed_rows)
            continue

        if journal_date is None:
            journal_date = datetime.utcnow()

        total_debit = sum((Decimal(str(l["debit"])) for l in lines), Decimal(0))
        total_credit = sum((Decimal(str(l["credit"])) for l in lines), Decimal(0))
        if total_debit != total_credit:
            result.errors.append(
                f"Journal {ref_no or _key} (rows {row_nums}): debits must equal credits"
            )
            result.skipped += len(indexed_rows)
            continue

        seq = await db.documentnumbersequence.find_unique(
            where={"companyId_key": {"companyId": company_id, "key": "journal"}}
        )
        next_no = seq.nextValue if seq else 1
        if seq:
            await db.documentnumbersequence.update(
                where={"companyId_key": {"companyId": company_id, "key": "journal"}},
                data={"nextValue": next_no + 1},
            )

        try:
            await repo.create_with_lines(
                company_id=company_id,
                journal_number=str(next_no),
                journal_date=journal_date,
                ref_no=ref_no,
                total_amount=total_debit,
                lines=lines,
                status=status,
            )
            result.created += 1
        except Exception as exc:  # noqa: BLE001
            result.errors.append(f"Journal {ref_no or _key}: {exc}")
            result.skipped += len(indexed_rows)

    return result
