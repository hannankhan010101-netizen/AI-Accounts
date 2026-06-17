"""Single source of truth for RBAC permission matrix — RBAC v2."""

from __future__ import annotations

from typing import Any

# Standard action columns for the permission matrix UI.
MATRIX_ACTIONS: tuple[str, ...] = (
    "view",
    "create",
    "edit",
    "delete",
    "approve",
    "export",
    "print",
    "import",
    "void",
    "manage_settings",
    "manage_users",
    "manage_roles",
    "api_access",
)

# Sensitive fields for field-level security.
FIELD_SECURITY_KEYS: tuple[dict[str, str], ...] = (
    {"key": "cost_price", "label": "Cost price"},
    {"key": "profit_margin", "label": "Profit margin"},
    {"key": "discount", "label": "Discounts"},
    {"key": "tax_rate", "label": "Tax rates"},
    {"key": "bank_account", "label": "Bank accounts"},
    {"key": "gl_account", "label": "GL accounts"},
    {"key": "credit_limit", "label": "Customer credit limits"},
)

FIELD_ACCESS_LEVELS: tuple[str, ...] = ("view", "edit", "hidden")

DATA_SCOPE_TYPES: tuple[str, ...] = (
    "customer",
    "supplier",
    "product",
    "location",
    "warehouse",
    "project",
    "company",
)


def _cell(module: str, resource: str, action: str, label: str, code: str) -> dict[str, str]:
    return {
        "module": module,
        "resource": resource,
        "action": action,
        "label": label,
        "code": code,
    }


# Matrix rows: module → resources → action → permission code
PERMISSION_MATRIX: list[dict[str, Any]] = [
    {
        "module": "sales",
        "moduleLabel": "Sales",
        "resources": [
            {
                "resource": "overview",
                "label": "Overview",
                "actions": {"view": "sales.read"},
            },
            {
                "resource": "customers",
                "label": "Customers",
                "actions": {
                    "view": "sales.customers.read",
                    "create": "sales.customers.create",
                    "edit": "sales.customers.create",
                },
            },
            {
                "resource": "quotations",
                "label": "Quotations",
                "actions": {
                    "view": "sales.quotations.read",
                    "create": "sales.quotations.create",
                    "edit": "sales.quotations.create",
                },
            },
            {
                "resource": "orders",
                "label": "Orders",
                "actions": {
                    "view": "sales.orders.read",
                    "create": "sales.orders.create",
                    "edit": "sales.orders.create",
                },
            },
            {
                "resource": "invoices",
                "label": "Invoices",
                "actions": {
                    "view": "sales.invoices.read",
                    "create": "sales.invoices.create",
                    "edit": "sales.invoices.create",
                    "approve": "sales.invoices.approve",
                },
            },
            {
                "resource": "receipts",
                "label": "Receipts",
                "actions": {
                    "view": "sales.receipts.read",
                    "create": "sales.receipts.create",
                    "edit": "sales.receipts.create",
                },
            },
            {
                "resource": "credits",
                "label": "Credits",
                "actions": {
                    "view": "sales.credits.read",
                    "create": "sales.credits.create",
                    "edit": "sales.credits.create",
                },
            },
            {
                "resource": "pdc",
                "label": "PDC received",
                "actions": {"view": "sales.pdc.read"},
            },
            {
                "resource": "all",
                "label": "All sales",
                "actions": {"view": "sales.*"},
            },
        ],
    },
    {
        "module": "purchases",
        "moduleLabel": "Purchases",
        "resources": [
            {"resource": "overview", "label": "Overview", "actions": {"view": "purchases.read"}},
            {
                "resource": "suppliers",
                "label": "Suppliers",
                "actions": {
                    "view": "purchases.suppliers.read",
                    "create": "purchases.suppliers.create",
                    "edit": "purchases.suppliers.create",
                },
            },
            {
                "resource": "orders",
                "label": "Purchase orders",
                "actions": {
                    "view": "purchases.orders.read",
                    "create": "purchases.orders.create",
                    "edit": "purchases.orders.create",
                },
            },
            {
                "resource": "bills",
                "label": "Supplier bills",
                "actions": {
                    "view": "purchases.bills.read",
                    "create": "purchases.bills.create",
                    "edit": "purchases.bills.create",
                    "approve": "purchases.bills.approve",
                },
            },
            {
                "resource": "payments",
                "label": "Payments",
                "actions": {
                    "view": "purchases.payments.read",
                    "create": "purchases.payments.create",
                    "edit": "purchases.payments.create",
                },
            },
            {
                "resource": "credits",
                "label": "Credits",
                "actions": {
                    "view": "purchases.credits.read",
                    "create": "purchases.credits.create",
                    "edit": "purchases.credits.create",
                },
            },
            {
                "resource": "grn",
                "label": "Goods received",
                "actions": {
                    "view": "purchases.grn.read",
                    "create": "purchases.grn.create",
                    "edit": "purchases.grn.create",
                },
            },
            {
                "resource": "pdc",
                "label": "PDC issued",
                "actions": {"view": "purchases.pdc.read"},
            },
            {"resource": "all", "label": "All purchases", "actions": {"view": "purchases.*"}},
        ],
    },
    {
        "module": "bank",
        "moduleLabel": "Banking",
        "resources": [
            {"resource": "overview", "label": "Overview", "actions": {"view": "bank.read"}},
            {
                "resource": "payments",
                "label": "Payments & receipts",
                "actions": {"create": "bank.payments.create", "edit": "bank.payments.create"},
            },
            {
                "resource": "reconciliation",
                "label": "Reconciliation",
                "actions": {
                    "view": "bank.reconciliation.create",
                    "create": "bank.reconciliation.create",
                    "edit": "bank.reconciliation.update",
                    "approve": "bank.reconciliation.complete",
                },
            },
            {"resource": "all", "label": "All bank", "actions": {"view": "bank.*"}},
        ],
    },
    {
        "module": "inventory",
        "moduleLabel": "Inventory",
        "resources": [
            {"resource": "overview", "label": "Overview", "actions": {"view": "inventory.read"}},
            {
                "resource": "products",
                "label": "Products",
                "actions": {
                    "view": "inventory.products.read",
                    "create": "inventory.products.create",
                    "edit": "inventory.products.create",
                },
            },
            {
                "resource": "adjustments",
                "label": "Stock adjustments",
                "actions": {"create": "inventory.adjustments.create", "approve": "inventory.adjustments.create"},
            },
            {"resource": "all", "label": "All inventory", "actions": {"view": "inventory.*"}},
        ],
    },
    {
        "module": "financial",
        "moduleLabel": "Financial & settings",
        "resources": [
            {
                "resource": "reports_financial",
                "label": "Financial reports",
                "actions": {"view": "reports.read", "export": "reports.*"},
            },
            {
                "resource": "journals",
                "label": "Journals",
                "actions": {
                    "create": "settings.journals.create",
                    "void": "settings.journals.reverse",
                    "delete": "settings.journals.delete",
                },
            },
            {
                "resource": "settings",
                "label": "Company settings",
                "actions": {
                    "view": "settings.read",
                    "manage_settings": "settings.content.manage",
                },
            },
            {
                "resource": "users",
                "label": "Users",
                "actions": {
                    "view": "settings.users.read",
                    "manage_users": "settings.users.invite",
                },
            },
            {
                "resource": "roles",
                "label": "Roles",
                "actions": {"manage_roles": "settings.roles.manage"},
            },
            {
                "resource": "access_control",
                "label": "Access control",
                "actions": {"manage_settings": "settings.access_control.manage"},
            },
            {
                "resource": "platform",
                "label": "Platform operator",
                "actions": {"manage_settings": "settings.platform.process"},
            },
        ],
    },
    {
        "module": "integrations",
        "moduleLabel": "Integrations",
        "resources": [
            {"resource": "fbr", "label": "FBR", "actions": {"view": "fbr.read", "create": "fbr.*"}},
            {"resource": "payments", "label": "Online payments", "actions": {"view": "payments.read", "create": "payments.*"}},
            {"resource": "assembly", "label": "Assembly", "actions": {"view": "assembly.read", "create": "assembly.jobs.create"}},
        ],
    },
    {
        "module": "global",
        "moduleLabel": "Global",
        "resources": [
            {"resource": "all", "label": "Full access", "actions": {"view": "*"}},
        ],
    },
]


def flatten_matrix_definitions() -> list[dict[str, Any]]:
    """All permission definition rows for DB seed."""
    rows: list[dict[str, Any]] = []
    order = 0
    for mod in PERMISSION_MATRIX:
        module = str(mod["module"])
        group_label = str(mod["moduleLabel"])
        for res in mod.get("resources", []):
            resource = str(res["resource"])
            res_label = str(res["label"])
            for action, code in (res.get("actions") or {}).items():
                order += 1
                rows.append(
                    {
                        "code": code,
                        "module": module,
                        "resource": resource,
                        "action": action,
                        "label": f"{res_label} — {action.replace('_', ' ').title()}",
                        "groupLabel": group_label,
                        "sortOrder": order,
                    }
                )
    return rows


def matrix_for_api() -> dict[str, Any]:
    """Payload for GET /permissions/matrix."""
    return {
        "actions": list(MATRIX_ACTIONS),
        "modules": PERMISSION_MATRIX,
        "fieldSecurityKeys": list(FIELD_SECURITY_KEYS),
        "fieldAccessLevels": list(FIELD_ACCESS_LEVELS),
        "dataScopeTypes": list(DATA_SCOPE_TYPES),
    }


def all_known_codes() -> frozenset[str]:
    return frozenset(row["code"] for row in flatten_matrix_definitions())


def parse_permission_code(code: str) -> tuple[str, str, str]:
    """Best-effort split of legacy dotted codes."""
    if code == "*":
        return "global", "all", "view"
    parts = code.split(".")
    if len(parts) == 1:
        return parts[0], "all", "view"
    if len(parts) == 2:
        return parts[0], parts[1], "view"
    return parts[0], parts[1], parts[2]
