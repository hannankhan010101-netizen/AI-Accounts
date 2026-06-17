"""Module code ↔ minimum RBAC permission — P12.

Users need the module entitlement enabled **and** at least one listed permission
(or ``*``) to pass ``require_module_access``.
"""

from __future__ import annotations

MODULE_PERMISSION_MATRIX: dict[str, tuple[str, ...]] = {
    "sales": (
        "sales.invoices.create",
        "sales.invoices.approve",
        "sales.customers.create",
        "sales.quotations.create",
        "sales.orders.create",
        "sales.receipts.create",
        "sales.credits.create",
        "sales.*",
    ),
    "purchases": (
        "purchases.bills.create",
        "purchases.bills.approve",
        "purchases.suppliers.create",
        "purchases.orders.create",
        "purchases.payments.create",
        "purchases.credits.create",
        "purchases.grn.create",
        "purchases.*",
    ),
    "bank": ("bank.payments.create", "bank.reconciliation.create", "bank.*"),
    "inventory": ("inventory.adjustments.create", "inventory.*"),
    "assembly": ("assembly.jobs.create", "assembly.*"),
    "projects": ("projects.*", "purchases.bills.create"),
    "financial": (
        "settings.journals.create",
        "settings.journals.reverse",
        "settings.users.invite",
        "reports.*",
    ),
    "fbr": ("sales.invoices.approve", "fbr.*"),
    "payments": ("bank.payments.create", "payments.*"),
}

PLAN_MODULE_DEFAULTS: dict[str, frozenset[str]] = {
    "standard": frozenset(MODULE_PERMISSION_MATRIX.keys()),
    "starter": frozenset({"sales", "purchases", "bank", "financial"}),
    "pro": frozenset(MODULE_PERMISSION_MATRIX.keys()),
    "past_due": frozenset({"financial"}),
    "cancelled": frozenset(),
}

# ``None`` = unlimited seats for that plan.
PLAN_SEAT_LIMITS: dict[str, int | None] = {
    "starter": 3,
    "standard": 10,
    "pro": None,
    "past_due": 10,
    "cancelled": 0,
}
