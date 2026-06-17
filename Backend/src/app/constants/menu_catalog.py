"""Content Settings menu targets — catalog §12.14 Menu branch."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MenuItemDef:
    href: str
    group: str
    label: str
    active: bool = True


MENU_CATALOG: tuple[MenuItemDef, ...] = (
    MenuItemDef("/dashboard", "Home", "Home"),
    MenuItemDef("/sales/invoices", "Sell", "Invoices"),
    MenuItemDef("/sales/quotations", "Sell", "Quotations"),
    MenuItemDef("/sales/orders", "Sell", "Orders"),
    MenuItemDef("/sales/credits", "Sell", "Credits"),
    MenuItemDef("/sales/receipts", "Sell", "Receipts"),
    MenuItemDef("/sales/delivery-notes", "Sell", "Delivery notes"),
    MenuItemDef("/sales/pdc-received", "Sell", "Cheques received"),
    MenuItemDef("/sales/all", "Sell", "All sales activity"),
    MenuItemDef("/sales/customers", "Sell", "Customers"),
    MenuItemDef("/purchases/orders", "Buy", "Purchase orders"),
    MenuItemDef("/purchases/bills", "Buy", "Supplier bills"),
    MenuItemDef("/purchases/credits", "Buy", "Credits"),
    MenuItemDef("/purchases/payments", "Buy", "Payments"),
    MenuItemDef("/purchases/pdc-issued", "Buy", "Cheques issued"),
    MenuItemDef("/purchases/grn", "Buy", "Goods received"),
    MenuItemDef("/purchases/all", "Buy", "All purchase activity"),
    MenuItemDef("/purchases/suppliers", "Buy", "Suppliers"),
    MenuItemDef("/bank/balances", "Money", "Account balances"),
    MenuItemDef("/bank/payments", "Money", "Payments out"),
    MenuItemDef("/bank/receipts", "Money", "Receipts in"),
    MenuItemDef("/bank/transfers", "Money", "Transfers"),
    MenuItemDef("/bank/reconciliation", "Money", "Reconciliation"),
    MenuItemDef("/inventory/products", "Stock", "Products"),
    MenuItemDef("/inventory/batches", "Stock", "Batches & expiry"),
    MenuItemDef("/reports", "Insights", "Reports"),
    MenuItemDef("/settings", "Admin", "Settings"),
)

MENU_BY_HREF: dict[str, MenuItemDef] = {m.href: m for m in MENU_CATALOG}


def default_menu_layout() -> dict[str, object]:
    return {
        "items": [
            {
                "href": m.href,
                "group": m.group,
                "label": m.label,
                "active": m.active,
                "order": i,
            }
            for i, m in enumerate(MENU_CATALOG)
        ],
    }
