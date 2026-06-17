#!/usr/bin/env python3
"""Deep FA vs AI parity — discovered links, catalog §15, attachment targets, dashboard widgets."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# FA §3.5 attachment targets
FA_ATTACHMENT_ENTITIES = {
    "bank_payment",
    "bank_receipt",
    "bank_transfer",
    "sales_invoice",
    "sales_order",
    "customer_receipt",
    "supplier_bill",
    "purchase_order",
    "supplier_payment",
    "journal",
}

# FA §10.9 dashboard widgets (from catalog)
FA_DASHBOARD_WIDGETS = [
    "AR Summary (aging buckets)",
    "AR Top 10",
    "AR Watchlist",
    "AP Summary (aging buckets)",
    "AP Top 10",
    "AP Watchlist",
    "Bank balances",
    "Bank balances watchlist",
    "Bank cash flow all (12mo)",
    "Bank cash flow watchlist",
    "Monthly bank balance all",
    "Monthly bank balance watchlist",
    "Products strip (low/out/oversold/in stock)",
    "Sales FY",
    "Expenses FY",
    "P&L FY",
]

# FA §12.1 settings links from discovered_links (Nafy-Pharma tenant)
FA_DISCOVERED_SETTINGS = {
    "Journals": "/settings/journals",
    "Nominals": "/settings/nominals",
    "Section Management": "/settings/sections",
    "Users Management": "/settings/users",
    "Roles Management": "/settings/roles",
    "Dashboard Management": "/settings/dashboards",
    "Lock Date": "/settings/lock-date",
    "OP Methods": "/settings/op-methods",
    "Log Management": "/settings/user-log",
    "Smart Settings": "/settings/smart",
    "Taxes and Year End": "/settings/taxes-year-end",
    "Business Information": "/settings/business-information",
    "Filters Management": "/settings/filters",
    "Column Management": "/settings/columns",
    "Content Settings": "/settings/content",
    "Missed Recurrence": "/settings/missed-recurrence",
    "Email Settings": "/settings/email",
    "Sent Emails": "/settings/sent-emails",
}

# FA add-ons in catalog but NOT in Nafy discovered settings (may be unlicensed)
FA_CATALOG_SETTINGS_NOT_IN_DISCOVER = [
    ("Budget", "/settings/budget", "§9.3 add-on"),
    ("Authorisation", "/settings/authorisation", "§12.6 add-on"),
    ("Location", "/settings/locations", "§12.7"),
    ("Advance Users", "/settings/advance-users", "§12.5 — route missing in AI"),
    ("Chart of Account", "/settings/coa", "§9.1.1 — FA has Nominals link only in discover"),
]

# FA §2.6 tutorial items not in Nafy sidebar discover
FA_TUTORIAL_ONLY = [
    "Stock Transfer",
    "Reports",
    "Analytical Reports",
    "Landed Cost",
    "Letter of Credit",
    "Multi Unit",
    "Batch and Expiry",
    "Bank Revaluation",
    "Multi Currency",
    "Assembly Jobs",
    "Assembly Templates",
    "Fixed Assets",
    "Consolidation",
    "Advance Users",
    "Budget",
    "Authorisation",
    "Location",
]

# Cross-cutting §3 features — behavioral
FA_BEHAVIOR_FEATURES = [
    ("Transaction templates", "partial", "missed-recurrence only sibling"),
    ("Recurring scheduler", "missing", "§3.3"),
    ("Copy SI / journal / bank payment", "partial", "§3.9"),
    ("Batch sales invoice", "missing", "§3.9"),
    ("Batch supplier bills", "missing", "§3.9"),
    ("Excel bank voucher import (EP/IR)", "missing", "§3.8"),
    ("Excel customer import", "missing", "§5.1"),
    ("Excel SI/SR import", "missing", "§5.4/§5.8"),
    ("Excel VI import", "missing", "§6.3"),
    ("Excel journal import", "missing", "§3.8"),
    ("Email invoice from SI", "missing", "§3.6"),
    ("SMS triggers", "missing", "§3.6"),
    ("Two-copy print SR/VP", "partial", "§3.7"),
    ("Journal print from transactional screens", "partial", "§3.7"),
    ("Bank voucher vs journal print choice", "partial", "§3.7"),
    ("Report drill-down hyperlinks", "partial", "§3.10"),
    ("Favorites star sync", "partial", "§10.2"),
    ("ADT/FED/WHT on document lines", "missing", "§3.12"),
    ("Per-user lock date", "partial", "§3.14"),
    ("FIFO allocation", "done", "§3.15"),
    ("Retail margin / trade offer", "missing", "§3.16"),
    ("Width x length area qty", "missing", "§3.17"),
    ("FBR live submit", "partial", "§3.18 stub"),
    ("PayPro live webhook", "partial", "§3.20 stub"),
    ("Email automation module", "missing", "§3.19"),
    ("Google Sign-In", "missing", "§1.1"),
    ("2FA", "missing", "§1.1"),
    ("API user type + OTP keys", "partial", "§1.4"),
    ("Forgot password OTP email", "partial", "§1.1"),
    ("Customer advance return", "partial", "§5.8"),
    ("Supplier advance return", "partial", "§6.4"),
    ("Multiple SOs -> one SI", "partial", "§5.3"),
    ("Edit SI/VI after partial payment", "partial", "§5.4/§6.3"),
    ("PDC bounce/reversal", "partial", "§5.7"),
    ("Bundle products", "missing", "§7.1"),
    ("Customer-product pricing lines", "missing", "§5.1"),
    ("Product bulk tax update", "missing", "§7.1"),
    ("Opening stock bulk import UI", "partial", "§7.1 migration script only"),
    ("Batch/expiry on SI/VI lines", "partial", "§7.8"),
    ("Authorisation runtime on posts", "partial", "§12.6"),
    ("Advance users data fence", "missing", "§12.5"),
    ("Vehicles module", "missing", "§12.4.2 RBAC only"),
    ("POS invoice mode", "missing", "§12.2.2 toggle exists, no POS UI"),
    ("E-signatures upload", "partial", "§12.2.4 accordion shell"),
    ("Fine daily / fine percentage", "missing", "§12.2.2"),
    ("Smart Filter/Doc labels on forms", "partial", "§12.2.3"),
    ("Auto-code generation runtime", "partial", "§12.2.8"),
    ("Dark mode", "missing", "§12.1 rail"),
    ("Notifications bell", "missing", "§15"),
    ("New Message (FA header)", "missing", "discovered_links"),
    ("Quick + Add SI / Add VI", "partial", "command palette not FAB"),
]


def read_text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def nav_hrefs() -> set[str]:
    nav = read_text("Frontend/src/config/navigation.ts")
    settings = read_text("Frontend/src/config/settings-menu.ts")
    return set(re.findall(r'href:\s*"([^"]+)"', nav + settings))


def pages_exist() -> set[str]:
    pages = {
        str(p.relative_to(ROOT)).replace("\\", "/")
        for p in (ROOT / "Frontend/src/app/(app)").rglob("page.tsx")
    }
    return pages


def has_page(href: str, pages: set[str]) -> bool:
    if href.startswith("/settings/printing/"):
        return "Frontend/src/app/(app)/settings/printing/[code]/page.tsx" in pages
    if href.startswith("/reports/extended/"):
        return "Frontend/src/app/(app)/reports/extended/[slug]/page.tsx" in pages
    path = href.strip("/")
    return f"Frontend/src/app/(app)/{path}/page.tsx" in pages


def scan_attachment_ui() -> set[str]:
    found: set[str] = set()
    for p in (ROOT / "Frontend/src").rglob("*.tsx"):
        try:
            t = p.read_text(encoding="utf-8")
        except OSError:
            continue
        if "AttachmentPanel" not in t:
            continue
        for m in re.finditer(r'entityType=["\']([^"\']+)["\']', t):
            found.add(m.group(1))
        for m in re.finditer(r"entityType:\s*['\"]([^'\"]+)['\"]", t):
            found.add(m.group(1))
    return found


def scan_dashboard_widgets() -> list[str]:
    t = read_text("Frontend/src/components/dashboard/business-overview.tsx")
    widgets = []
    if "ar-summary" in t or "ArSummary" in t or "AR" in t:
        widgets.append("AR Summary")
    if "ap-summary" in t:
        widgets.append("AP Summary")
    if "bank-balances" in t:
        widgets.append("Bank balances")
    if "bankCashFlow" in t or "Bank cash flow" in t:
        widgets.append("Bank cash flow 12mo")
    if "inventoryStock" in t or "InventoryStatus" in t:
        widgets.append("Products strip")
    if "salesByMonth" in t:
        widgets.append("Sales FY chart")
    if "profitAndLoss" in t or "P&L" in t or "netProfit" in t:
        widgets.append("P&L FY")
    if "watchlist" in t.lower():
        widgets.append("Watchlists")
    if "top10" in t.lower() or "Top 10" in t:
        widgets.append("Top 10")
    return widgets


def count_report_ids() -> tuple[int, list[str]]:
    text = read_text("Backend/src/app/constants/report_definitions.py")
    ids = re.findall(r'"id"\s*:\s*"([^"]+)"', text)
    if not ids:
        ids = re.findall(r'id:\s*"([^"]+)"', text)
    return len(ids), sorted(set(ids))[:10]


def main() -> int:
    hrefs = nav_hrefs()
    pages = pages_exist()
    att_ui = scan_attachment_ui()
    dash = scan_dashboard_widgets()
    rep_count, rep_sample = count_report_ids()

    print("=" * 70)
    print("DEEP PARITY CHECK — FastAccounts vs AI-Accounts")
    print("=" * 70)

    print("\n## 1. Nafy-Pharma FA discovered settings links")
    for label, route in FA_DISCOVERED_SETTINGS.items():
        ok = route in hrefs and has_page(route, pages)
        print(f"  {'OK' if ok else 'GAP':3}  {label:28} {route}")

    print("\n## 2. FA catalog settings NOT in Nafy discover (verify license)")
    for label, route, note in FA_CATALOG_SETTINGS_NOT_IN_DISCOVER:
        ok = route in hrefs and has_page(route, pages)
        print(f"  {'OK' if ok else 'GAP':3}  {label:28} {route}  ({note})")

    print("\n## 3. FA §3.5 attachments — UI entityType coverage")
    # Map FA entities to AI entity types (best effort)
    ai_to_fa = {
        "sales_invoice": "sales_invoice",
        "sales_order": "sales_order",
        "supplier_bill": "supplier_bill",
        "purchase_order": "purchase_order",
        "sales_receipt": "customer_receipt",
        "supplier_payment": "supplier_payment",
        "bank_payment": "bank_payment",
        "bank_receipt": "bank_receipt",
        "bank_transfer": "bank_transfer",
        "journal": "journal",
    }
    for fa_ent in sorted(FA_ATTACHMENT_ENTITIES):
        ai_keys = [k for k, v in ai_to_fa.items() if v == fa_ent]
        covered = any(k in att_ui for k in ai_keys)
        print(f"  {'OK' if covered else 'GAP':3}  {fa_ent:22} UI types={ai_keys or ['?']} found={covered}")
    if att_ui:
        print(f"  AttachmentPanel entity types in codebase: {sorted(att_ui)}")

    print("\n## 4. Dashboard §10.9 widgets (AI implementation scan)")
    for w in FA_DASHBOARD_WIDGETS:
        impl = any(
            k in " ".join(dash).lower()
            for k in w.lower().split()[:2]
        )
        # manual overrides
        if "AR Summary" in w and "AR Summary" in dash:
            impl = True
        if "AP Summary" in w and "AP Summary" in dash:
            impl = True
        if "Bank balances" in w and "Bank balances" in dash:
            impl = True
        if "Bank cash flow" in w and "Bank cash flow" in dash:
            impl = True
        if "Products strip" in w and "Products strip" in dash:
            impl = True
        if "Sales FY" in w and "Sales FY" in dash:
            impl = True
        if "P&L" in w and "P&L FY" in dash:
            impl = True
        if "Top 10" in w and "Top 10" in dash:
            impl = True
        if "Watchlist" in w and "Watchlists" in dash:
            impl = False  # UX doc says placeholder
        if "Monthly bank balance" in w:
            impl = False
        if "Expenses FY" in w and "P&L FY" in dash:
            impl = True  # partial via donut
        print(f"  {'OK' if impl else 'GAP':3}  {w}")
    print(f"  Detected widget keys: {dash}")

    print("\n## 5. Reports backend catalog")
    print(f"  Definition rows: {rep_count} (sample ids: {rep_sample}...)")

    print("\n## 6. Behavioral gaps (§3 cross-cutting) — status summary")
    counts = {"done": 0, "partial": 0, "missing": 0}
    for name, status, ref in FA_BEHAVIOR_FEATURES:
        counts[status] = counts.get(status, 0) + 1
        mark = {"done": "OK ", "partial": "PRT", "missing": "GAP"}[status]
        print(f"  {mark}  {name:42} {ref}")
    print(f"\n  Behavioral: done={counts.get('done',0)} partial={counts.get('partial',0)} missing={counts.get('missing',0)}")

    print("\n## 7. FA tutorial §2.6 items — AI nav routes")
    tutorial_routes = {
        "Stock Transfer": "/inventory/stock-transfer",
        "Reports": "/reports",
        "Analytical Reports": "/reports/analytical",
        "Batch and Expiry": "/inventory/batches",
        "Assembly Jobs": "/inventory/assembly/jobs",
        "Assembly Templates": "/inventory/assembly/templates",
        "Bank Revaluation": "/bank/fx-revaluation",
        "Budget": "/settings/budget",
        "Authorisation": "/settings/authorisation",
        "Location": "/settings/locations",
    }
    for item in FA_TUTORIAL_ONLY:
        route = tutorial_routes.get(item)
        if route:
            ok = route in hrefs and has_page(route, pages)
            print(f"  {'OK' if ok else 'GAP':3}  {item:28} {route}")
        else:
            print(f"  GAP  {item:28} — no route")

    return 0


if __name__ == "__main__":
    sys.exit(main())
