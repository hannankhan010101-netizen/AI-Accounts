"""Permission tree and list-read codes — P25 / FA §12.4 expanded submodules."""

from __future__ import annotations

from typing import Any

# Minimum permission for GET list grids (module must also be enabled).
MODULE_LIST_READ_PERMISSIONS: dict[str, tuple[str, ...]] = {
    "sales": (
        "sales.read",
        "sales.customers.read",
        "sales.invoices.read",
        "sales.orders.read",
        "sales.quotations.read",
        "sales.receipts.read",
        "sales.credits.read",
        "sales.*",
        "*",
    ),
    "purchases": (
        "purchases.read",
        "purchases.suppliers.read",
        "purchases.bills.read",
        "purchases.orders.read",
        "purchases.payments.read",
        "purchases.credits.read",
        "purchases.grn.read",
        "purchases.*",
        "*",
    ),
    "bank": ("bank.read", "bank.*", "*"),
    "inventory": ("inventory.read", "inventory.products.read", "inventory.*", "*"),
    "financial": ("reports.read", "settings.read", "settings.users.read", "reports.*", "*"),
    "assembly": ("assembly.read", "assembly.*", "*"),
    "fbr": ("fbr.read", "fbr.*", "*"),
    "payments": ("payments.read", "payments.*", "*"),
}

_PERM = lambda code, label: {"code": code, "label": label}  # noqa: E731


def _sub(name: str, permissions: list[dict[str, str]]) -> dict[str, Any]:
    return {"name": name, "permissions": permissions}


def flatten_permission_entries(tree: list[dict[str, Any]] | None = None) -> list[dict[str, str]]:
    """All permission rows from the tree (group-level + submodule)."""

    rows: list[dict[str, str]] = []
    for group in tree or PERMISSION_TREE:
        for entry in group.get("permissions", []):
            rows.append({"code": str(entry["code"]), "label": str(entry["label"])})
        for sub in group.get("submodules", []):
            for entry in sub.get("permissions", []):
                rows.append({"code": str(entry["code"]), "label": str(entry["label"])})
    return rows


PERMISSION_TREE: list[dict[str, Any]] = [
    {
        "group": "Sales",
        "submodules": [
            _sub("Overview", [_PERM("sales.read", "View sales lists and documents")]),
            _sub(
                "Customers",
                [
                    _PERM("sales.customers.read", "View customers"),
                    _PERM("sales.customers.create", "Create / edit customers"),
                ],
            ),
            _sub(
                "Quotations",
                [
                    _PERM("sales.quotations.read", "View quotations"),
                    _PERM("sales.quotations.create", "Create / edit quotations"),
                ],
            ),
            _sub(
                "Orders",
                [
                    _PERM("sales.orders.read", "View sales orders"),
                    _PERM("sales.orders.create", "Create / edit sales orders"),
                ],
            ),
            _sub(
                "Invoices",
                [
                    _PERM("sales.invoices.read", "View sales invoices"),
                    _PERM("sales.invoices.create", "Create / edit invoices"),
                    _PERM("sales.invoices.approve", "Approve / post / goods issue"),
                ],
            ),
            _sub(
                "Receipts",
                [
                    _PERM("sales.receipts.read", "View customer receipts"),
                    _PERM("sales.receipts.create", "Create customer receipts"),
                ],
            ),
            _sub(
                "Credits",
                [
                    _PERM("sales.credits.read", "View sales credits"),
                    _PERM("sales.credits.create", "Create sales credits"),
                ],
            ),
            _sub(
                "PDC received",
                [_PERM("sales.pdc.read", "View post-dated cheques received")],
            ),
            _sub("All sales", [_PERM("sales.*", "All sales permissions")]),
        ],
        "permissions": [],
    },
    {
        "group": "Purchases",
        "submodules": [
            _sub("Overview", [_PERM("purchases.read", "View purchases lists and documents")]),
            _sub(
                "Suppliers",
                [
                    _PERM("purchases.suppliers.read", "View suppliers"),
                    _PERM("purchases.suppliers.create", "Create / edit suppliers"),
                ],
            ),
            _sub(
                "Purchase orders",
                [
                    _PERM("purchases.orders.read", "View purchase orders"),
                    _PERM("purchases.orders.create", "Create / edit purchase orders"),
                ],
            ),
            _sub(
                "Supplier bills",
                [
                    _PERM("purchases.bills.read", "View supplier bills"),
                    _PERM("purchases.bills.create", "Create / edit supplier bills"),
                    _PERM("purchases.bills.approve", "Approve / post supplier bills"),
                ],
            ),
            _sub(
                "Payments",
                [
                    _PERM("purchases.payments.read", "View supplier payments"),
                    _PERM("purchases.payments.create", "Create supplier payments"),
                ],
            ),
            _sub(
                "Credits",
                [
                    _PERM("purchases.credits.read", "View purchase credits"),
                    _PERM("purchases.credits.create", "Create purchase credits"),
                ],
            ),
            _sub(
                "Goods received",
                [
                    _PERM("purchases.grn.read", "View goods receipt notes"),
                    _PERM("purchases.grn.create", "Create goods receipt notes"),
                ],
            ),
            _sub(
                "PDC issued",
                [_PERM("purchases.pdc.read", "View post-dated cheques issued")],
            ),
            _sub("All purchases", [_PERM("purchases.*", "All purchases permissions")]),
        ],
        "permissions": [],
    },
    {
        "group": "Bank",
        "submodules": [
            _sub("Overview", [_PERM("bank.read", "View bank lists")]),
            _sub(
                "Payments & receipts",
                [_PERM("bank.payments.create", "Bank payments / receipts / transfers")],
            ),
            _sub(
                "Reconciliation",
                [
                    _PERM("bank.reconciliation.create", "Start reconciliation sessions"),
                    _PERM("bank.reconciliation.update", "Tick / untick statement lines"),
                    _PERM("bank.reconciliation.complete", "Complete reconciliation"),
                ],
            ),
            _sub("All bank", [_PERM("bank.*", "All bank permissions")]),
        ],
        "permissions": [],
    },
    {
        "group": "Inventory",
        "submodules": [
            _sub("Overview", [_PERM("inventory.read", "View inventory lists")]),
            _sub(
                "Products",
                [
                    _PERM("inventory.products.read", "View products"),
                    _PERM("inventory.products.create", "Create / edit products"),
                ],
            ),
            _sub(
                "Adjustments",
                [_PERM("inventory.adjustments.create", "Stock adjustments / transfers")],
            ),
            _sub("All inventory", [_PERM("inventory.*", "All inventory permissions")]),
        ],
        "permissions": [],
    },
    {
        "group": "Financial",
        "submodules": [
            _sub("Reports", [_PERM("reports.read", "View / run reports")]),
            _sub(
                "Journals",
                [
                    _PERM("settings.journals.create", "Create journals"),
                    _PERM("settings.journals.reverse", "Reverse / void journals"),
                ],
            ),
            _sub(
                "Settings",
                [
                    _PERM("settings.read", "View settings"),
                    _PERM("settings.content.manage", "Content / listing / menu settings"),
                    _PERM("settings.smart.manage", "Smart settings"),
                ],
            ),
            _sub(
                "Users & roles",
                [
                    _PERM("settings.users.read", "View users / audit log"),
                    _PERM("settings.users.invite", "Invite users to company"),
                    _PERM("settings.roles.manage", "Manage roles"),
                    _PERM("settings.access_control.manage", "Manage access control"),
                ],
            ),
            _sub(
                "Platform",
                [_PERM("settings.platform.process", "Operator / platform tasks")],
            ),
            _sub("All reports", [_PERM("reports.*", "All report permissions")]),
        ],
        "permissions": [],
    },
    {
        "group": "Integrations",
        "submodules": [
            _sub("FBR", [_PERM("fbr.read", "View FBR status"), _PERM("fbr.*", "FBR submit / poll")]),
            _sub(
                "Online payments",
                [_PERM("payments.read", "View payment transactions"), _PERM("payments.*", "Online payments")],
            ),
            _sub(
                "Assembly",
                [_PERM("assembly.read", "View assembly"), _PERM("assembly.*", "Assembly jobs")],
            ),
        ],
        "permissions": [],
    },
    {
        "group": "Global",
        "permissions": [{"code": "*", "label": "Full access (Administrator)"}],
        "submodules": [],
    },
]
