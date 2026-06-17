#!/usr/bin/env python3
"""Compare FastAccounts catalog modules vs AI-Accounts navigation + gaps."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "fastaccounts_export"))

from modules_manifest import MODULES, SETTINGS_MODULES  # type: ignore

NAV_TEXT = (ROOT / "Frontend/src/config/navigation.ts").read_text(encoding="utf-8")
SETTINGS_TEXT = (ROOT / "Frontend/src/config/settings-menu.ts").read_text(encoding="utf-8")
PAGES = {
    str(p.relative_to(ROOT)).replace("\\", "/")
    for p in (ROOT / "Frontend/src/app/(app)").rglob("page.tsx")
}


def nav_hrefs() -> set[str]:
    return set(re.findall(r'href:\s*"([^"]+)"', NAV_TEXT))


def has_page(href: str) -> bool:
    if href.startswith("/reports/extended/"):
        return "Frontend/src/app/(app)/reports/extended/[slug]/page.tsx" in PAGES
    if href.startswith("/settings/printing/"):
        return "Frontend/src/app/(app)/settings/printing/[code]/page.tsx" in PAGES
    path = href.strip("/")
    if not path:
        return False
    return f"Frontend/src/app/(app)/{path}/page.tsx" in PAGES


# FA sidebar labels from modules_manifest (operational)
FA_SIDEBAR = {m.label: m.key for m in MODULES if m.category != "overview"}

# Map FA label -> expected AI nav label (catalogLabel or label)
FA_TO_AI: dict[str, tuple[str, str]] = {
    "Dashboard": ("Home", "/dashboard"),
    "Account Balances": ("Account balances", "/bank/balances"),
    "Bank Payments": ("Payments out", "/bank/payments"),
    "Bank Receipts": ("Receipts in", "/bank/receipts"),
    "Transfers": ("Transfers", "/bank/transfers"),
    "Reconciliation": ("Reconciliation", "/bank/reconciliation"),
    "Import Statement": ("Import statement", "/bank/import-statement"),
    "Invoices": ("Invoices", "/sales/invoices"),
    "Receipts": ("Receipts", "/sales/receipts"),
    "Post Dated Cheque Received": ("Cheques received", "/sales/pdc-received"),
    "Sales All": ("All sales activity", "/sales/all"),
    "Orders": ("Orders", "/sales/orders"),
    "Customers": ("Customers", "/sales/customers"),
    "Bills": ("Supplier bills", "/purchases/bills"),
    "Payments": ("Payments", "/purchases/payments"),
    "Post Dated Cheque Issued": ("Cheques issued", "/purchases/pdc-issued"),
    "Purchases All": ("All purchase activity", "/purchases/all"),
    "PO": ("Purchase orders", "/purchases/orders"),
    "Suppliers": ("Suppliers", "/purchases/suppliers"),
    "Products": ("Products", "/inventory/products"),
    "Stock Adjustment": ("Stock adjustment", "/inventory/stock-adjustment"),
    "Stock Transfer": ("Stock transfer", "/inventory/stock-transfer"),
    "Reports": ("Reports", "/reports"),
    "Analytical Reports": ("Analytical reports", "/reports/analytical"),
}

# FA tutorial-only / add-on modules NOT in live FA sidebar capture §2.1
FA_TUTORIAL_OR_ADDON = [
    ("Quotations", "/sales/quotations", "sidebar", "In Sales help; AI has dedicated nav"),
    ("Delivery notes", "/sales/delivery-notes", "sidebar", "GDNSI/GDNSO — AI has nav"),
    ("Goods received (GRN)", "/purchases/grn", "sidebar", "GRNPO/GRNVI"),
    ("Batches & Expiry", "/inventory/batches", "inventory", "Tutorial map; AI has nav"),
    ("Assembly Jobs", "/inventory/assembly/jobs", "inventory", "§11 ops UI"),
    ("Assembly Templates", "/inventory/assembly/templates", "inventory", "§11 ops UI"),
    ("Bank Revaluation", "/bank/fx-revaluation", "bank", "Page exists; wizard depth TBD"),
    ("Projects", "/settings/projects", "settings", "Master CRUD; line tagging partial"),
    ("Locations", "/settings/locations", "settings", "Multi-location masters"),
    ("Budget", "/settings/budget", "settings", "CRUD; import/compare reports TBD"),
    ("Authorisation", "/settings/authorisation", "settings", "Policy UI; runtime gates partial"),
    ("Landed Cost", None, "missing", "Tutorial §2.6 — no AI route"),
    ("Letter of Credit", None, "missing", "Tutorial §2.6 — no AI route"),
    ("Fixed Assets", None, "missing", "Add-on module §8"),
    ("Consolidation", None, "missing", "Reports tree §10.10.1"),
    ("Vehicles", None, "missing", "FA RBAC module §12.4.2 only"),
    ("Advance Users", None, "missing", "§12.5 — no /settings/advance-users route"),
    ("Multi Unit", None, "partial", "Product fields; no dedicated screen"),
    ("Bank Multi Currency", None, "partial", "FX page; bank setup wizard TBD"),
    ("Online payments", "/settings/online-payments", "settings", "PayPro config stub"),
    ("SMS module", None, "missing", "§3.6 — no SMS settings/credits UI"),
    ("Email triggers", "/settings/email", "settings", "Settings UI; dispatch TBD"),
    ("2FA / Google Sign-In", None, "auth", "Not in AI auth UI"),
    ("Dark mode", None, "chrome", "§12.1 right rail — not implemented"),
    ("Notifications bell", None, "chrome", "§15 global chrome"),
    ("Batch sales invoice", None, "missing", "Cross-cutting §3.9"),
    ("Batch supplier bills", None, "missing", "Cross-cutting §3.9"),
    ("Recurring transactions", "/settings/missed-recurrence", "partial", "Missed recurrence only"),
    ("Transaction templates", None, "missing", "Save layout reuse §3.3"),
    ("Excel bank voucher import", None, "partial", "Statement import yes; EP/IR Excel TBD"),
    ("Attachments on docs", None, "partial", "Sales/purch/logistics yes; bank/journal TBD"),
    ("FBR Digital invoicing", "/settings/fbr-errors", "settings", "FBR errors dashboard; live submit stub"),
    ("API users / IP restrict", "/settings/users", "partial", "Users; API user type TBD"),
    ("POS invoices", None, "missing", "Smart Settings Others toggle §12.2.2"),
]

CROSS_CUTTING = [
    ("Header: My Tasks", "/my-tasks", "done"),
    ("Header: Support", "/support", "done"),
    ("Header: Profile", "/profile", "done"),
    ("Header: Change password", "/profile/change-password", "done"),
    ("Header: Activity log", "/settings/user-log", "done"),
    ("Settings mega-menu (52 links)", "settings", "done", "0 stubs per route audit"),
    ("Print templates (22)", "/settings/printing/si", "done", "Dynamic [code] pages"),
    ("Report catalog browser", "/reports/catalog", "done"),
    ("Generic report runner", "/reports/run/[id]", "done"),
    ("Listing layouts wired", "content", "done", "6 key list pages"),
]


def main() -> int:
    hrefs = nav_hrefs()
    print("=" * 60)
    print("SIDEBAR PARITY (FastAccounts §2.1 vs AI-Accounts nav)")
    print("=" * 60)
    ok = 0
    miss = 0
    for fa_label, (ai_label, expected_href) in FA_TO_AI.items():
        if expected_href in hrefs and has_page(expected_href):
            print(f"  OK  {fa_label:30} -> {expected_href}")
            ok += 1
        else:
            print(f"  GAP {fa_label:30} -> {expected_href} (missing nav/page)")
            miss += 1
    print(f"\nSidebar: {ok}/{ok+miss} routes with pages\n")

    print("=" * 60)
    print("SETTINGS (FA settings modules vs AI)")
    print("=" * 60)
    settings_hrefs = set(re.findall(r'href:\s*"([^"]+)"', SETTINGS_TEXT))
    s_ok = sum(1 for h in settings_hrefs if has_page(h))
    s_stub = [h for h in settings_hrefs if not has_page(h)]
    print(f"  Settings links with page: {s_ok}/{len(settings_hrefs)}")
    if s_stub:
        print("  Stubs:", ", ".join(s_stub[:5]), "..." if len(s_stub) > 5 else "")

    print("\n" + "=" * 60)
    print("FA TUTORIAL / ADD-ON GAPS (not in FA §2.1 sidebar)")
    print("=" * 60)
    for name, href, kind, note in FA_TUTORIAL_OR_ADDON:
        status = "done" if href and has_page(href) else ("partial" if href else "missing")
        mark = {"done": "OK ", "partial": "PRT", "missing": "GAP"}[status]
        href_s = href or "—"
        print(f"  {mark}  {name:28} {href_s:35} {note}")

    print("\n" + "=" * 60)
    print("CROSS-CUTTING (recent waves)")
    print("=" * 60)
    for row in CROSS_CUTTING:
        name, href, status, *rest = row
        mark = "OK " if status == "done" else "GAP"
        print(f"  {mark}  {name}")

    print("\n" + "=" * 60)
    print("REPORTS")
    print("=" * 60)
    print("  Catalog API: ~84 definition rows, 59 numeric IDs with SQL handlers")
    print("  Dedicated UI pages: 29 in reports-catalog + extended slugs + run/[id]")
    print("  Analytical hub: all IDs link (dedicated or /reports/run/{id})")
    print("  Gap: ~25+ report defs return 'not implemented' placeholder rows")

    print("\n" + "=" * 60)
    print("MIGRATED DATA (Nafy-Pharma)")
    print("=" * 60)
    print("  Customers, suppliers, products, invoices, receipts, bills, payments,")
    print("  bank payments, journals — migrated; parity is feature/UI not row count.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
