"""Content Settings form field targets — catalog §12.14 Forms branch."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FormFieldDef:
    key: str
    label: str
    active: bool = True


@dataclass(frozen=True, slots=True)
class FormDef:
    id: str
    label: str
    branch: str
    fields: tuple[FormFieldDef, ...]


FORM_CATALOG: tuple[FormDef, ...] = (
    FormDef(
        "sales-invoice",
        "Sales invoice form",
        "Sales Forms",
        (
            FormFieldDef("invoiceDate", "Invoice date"),
            FormFieldDef("customerId", "Customer"),
            FormFieldDef("lines", "Line grid"),
            FormFieldDef("projectCode", "Project (lines)"),
            FormFieldDef("batchExpiry", "Batch / expiry (lines)"),
            FormFieldDef("smartFilters", "Smart filters"),
        ),
    ),
    FormDef(
        "supplier-bill",
        "Supplier bill form",
        "Purchase Forms",
        (
            FormFieldDef("billDate", "Bill date"),
            FormFieldDef("supplierId", "Supplier"),
            FormFieldDef("lines", "Line grid"),
            FormFieldDef("batchExpiry", "Batch / expiry (lines)"),
            FormFieldDef("smartFilters", "Smart filters"),
        ),
    ),
    FormDef(
        "sales-receipt",
        "Sales receipt form",
        "Sales Forms",
        (
            FormFieldDef("receiptDate", "Receipt date"),
            FormFieldDef("customerId", "Customer"),
            FormFieldDef("bankAccountId", "Bank account"),
            FormFieldDef("totalAmount", "Amount"),
            FormFieldDef("wht", "Withholding tax"),
            FormFieldDef("allocations", "Invoice allocations"),
            FormFieldDef("smartFilters", "Smart filters"),
        ),
    ),
    FormDef(
        "supplier-payment",
        "Supplier payment form",
        "Purchase Forms",
        (
            FormFieldDef("paymentDate", "Payment date"),
            FormFieldDef("supplierId", "Supplier"),
            FormFieldDef("bankAccountId", "Bank account"),
            FormFieldDef("totalAmount", "Amount"),
            FormFieldDef("wht", "Withholding tax"),
            FormFieldDef("allocations", "Bill allocations"),
            FormFieldDef("smartFilters", "Smart filters"),
        ),
    ),
    FormDef(
        "bank-payment",
        "Bank payment form",
        "Bank Forms",
        (
            FormFieldDef("paymentDate", "Payment date"),
            FormFieldDef("bankAccountId", "Bank account"),
            FormFieldDef("nominalCode", "Nominal"),
            FormFieldDef("nominalLines", "Split nominals"),
            FormFieldDef("totalAmount", "Amount"),
            FormFieldDef("smartFilters", "Smart filters"),
        ),
    ),
)

FORM_BY_ID: dict[str, FormDef] = {f.id: f for f in FORM_CATALOG}


def default_form_layout(form_id: str) -> dict[str, object]:
    row = FORM_BY_ID.get(form_id)
    if row is None:
        return {"formId": form_id, "fields": []}
    return {
        "formId": form_id,
        "fields": [
            {"key": f.key, "label": f.label, "active": f.active, "order": i}
            for i, f in enumerate(row.fields)
        ],
    }
