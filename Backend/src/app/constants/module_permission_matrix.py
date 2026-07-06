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
    "inventory": (
        "inventory.adjustments.create",
        "inventory.products.create",
        "inventory.products.read",
        "inventory.*",
    ),
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

# --- Write gate ------------------------------------------------------------
# ``MODULE_PERMISSION_MATRIX`` above is the *visibility* matrix: holding ANY of
# these (read OR write) means the module is shown in nav / the access matrix.
# But ``require_module_access`` guards MUTATING routes, so it must not be
# satisfied by a read-only permission. These codes convey read/report access
# only and are therefore stripped from the write gate (RBAC audit fix): a
# viewer with ``inventory.products.read`` or a reporting role with ``reports.*``
# must not be able to create products or post journals.
_READ_ONLY_PERMISSIONS: frozenset[str] = frozenset(
    {
        "inventory.products.read",
        "reports.*",
    }
)

# Used by ModuleAccessService.assert_access (require_module_access). Kept in sync
# with the visibility matrix automatically — just minus the read-only codes.
MODULE_WRITE_PERMISSIONS: dict[str, tuple[str, ...]] = {
    module: tuple(p for p in perms if p not in _READ_ONLY_PERMISSIONS)
    for module, perms in MODULE_PERMISSION_MATRIX.items()
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
