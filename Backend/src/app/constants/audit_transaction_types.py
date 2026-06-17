"""FA §12.15 User Log transaction type filter catalog."""

from __future__ import annotations

from dataclasses import dataclass

from app.constants.rbac_audit_types import RBAC_AUDIT_TYPES_SORTED


@dataclass(frozen=True, slots=True)
class AuditTransactionTypeDef:
    id: str
    label: str
    group: str


def _rows(group: str, pairs: tuple[tuple[str, str], ...]) -> tuple[AuditTransactionTypeDef, ...]:
    return tuple(AuditTransactionTypeDef(id=wid, label=label, group=group) for wid, label in pairs)


AUDIT_TRANSACTION_TYPE_CATALOG: tuple[AuditTransactionTypeDef, ...] = (
    *_rows(
        "Sales",
        (
            ("SALES_INVOICE", "Sales invoice"),
            ("SALES_ORDER", "Sales order"),
            ("SALES_RECEIPT", "Sales receipt"),
            ("SALES_CREDIT", "Sales credit note"),
            ("QUOTATION", "Quotation"),
            ("PDC_RECEIVED", "PDC received"),
            ("SI_VOID", "Sales invoice void"),
            ("SO_VOID", "Sales order void"),
        ),
    ),
    *_rows(
        "Purchases",
        (
            ("SUPPLIER_BILL", "Supplier bill"),
            ("PURCHASE_ORDER", "Purchase order"),
            ("SUPPLIER_PAYMENT", "Supplier payment"),
            ("SUPPLIER_CREDIT", "Supplier credit note"),
            ("GRN", "Goods receipt (GRN)"),
            ("GRN_VOID", "GRN void"),
            ("PDC_ISSUED", "PDC issued"),
            ("VI_VOID", "Supplier bill void"),
            ("PO_VOID", "Purchase order void"),
        ),
    ),
    *_rows(
        "Bank",
        (
            ("BANK_PAYMENT", "Bank payment"),
            ("BANK_RECEIPT", "Bank receipt"),
            ("BANK_TRANSFER", "Bank transfer"),
            ("BANK_RECONCILIATION", "Bank reconciliation"),
        ),
    ),
    *_rows(
        "Inventory & GL",
        (
            ("STOCK_ADJUSTMENT", "Stock adjustment"),
            ("GOODS_ISSUE", "Goods issue"),
            ("MANUAL_JOURNAL", "Manual journal"),
            ("ASSEMBLY_JOB", "Assembly job"),
            ("FX_REVALUATION", "FX revaluation"),
        ),
    ),
    *_rows(
        "Users & roles",
        tuple((t, t.replace("_", " ").title()) for t in RBAC_AUDIT_TYPES_SORTED),
    ),
    *_rows(
        "Security",
        (
            ("LOGIN", "Log in"),
            ("LOGOUT", "Log out"),
        ),
    ),
    *_rows(
        "Assistant",
        (
            ("assistant.query", "Assistant query"),
            ("assistant.tool", "Assistant tool (prefix)"),
        ),
    ),
)


def audit_transaction_type_groups() -> list[dict[str, object]]:
    groups: dict[str, list[dict[str, str]]] = {}
    for row in AUDIT_TRANSACTION_TYPE_CATALOG:
        groups.setdefault(row.group, []).append({"id": row.id, "label": row.label})
    return [{"group": g, "types": types} for g, types in groups.items()]
