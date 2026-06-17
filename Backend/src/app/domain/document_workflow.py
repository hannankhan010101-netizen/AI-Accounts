"""Unified document lifecycle — enterprise P0 state machine.

Operational monetary documents progress: draft → posted.
Settlement documents (receipts/payments) post immediately in this slice.
"""

from __future__ import annotations

from typing import Final

# Canonical workflow states
DRAFT: Final[str] = "draft"
POSTED: Final[str] = "posted"
VOIDED: Final[str] = "voided"
REVERSED: Final[str] = "reversed"

# Document kinds (for journal traceability)
SOURCE_SALES_INVOICE: Final[str] = "SALES_INVOICE"
SOURCE_SUPPLIER_BILL: Final[str] = "SUPPLIER_BILL"
SOURCE_STOCK_ADJUSTMENT: Final[str] = "STOCK_ADJUSTMENT"
SOURCE_SALES_CREDIT: Final[str] = "SALES_CREDIT"
SOURCE_SUPPLIER_CREDIT: Final[str] = "SUPPLIER_CREDIT"
SOURCE_SALES_RECEIPT: Final[str] = "SALES_RECEIPT"
SOURCE_SUPPLIER_PAYMENT: Final[str] = "SUPPLIER_PAYMENT"
SOURCE_BANK_PAYMENT: Final[str] = "BANK_PAYMENT"
SOURCE_BANK_RECEIPT: Final[str] = "BANK_RECEIPT"
SOURCE_BANK_TRANSFER: Final[str] = "BANK_TRANSFER"
SOURCE_BANK_RECONCILIATION: Final[str] = "BANK_RECONCILIATION"
SOURCE_MANUAL_JOURNAL: Final[str] = "MANUAL_JOURNAL"
SOURCE_SALES_INVOICE_COGS: Final[str] = "SALES_INVOICE_COGS"
SOURCE_GOODS_ISSUE: Final[str] = "GOODS_ISSUE"
SOURCE_ASSEMBLY_JOB: Final[str] = "ASSEMBLY_JOB"
SOURCE_FX_REVALUATION: Final[str] = "FX_REVALUATION"

_ALLOWED_POST_TRANSITIONS: dict[str, set[str]] = {
    DRAFT: {POSTED},
    POSTED: {VOIDED, REVERSED},
}


def assert_can_transition(*, current: str, target: str) -> None:
    """Raise ``ValueError`` when ``target`` is not allowed from ``current``."""

    allowed = _ALLOWED_POST_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise ValueError(f"Cannot transition document from '{current}' to '{target}'")
