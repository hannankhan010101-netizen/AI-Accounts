"""Verify Wave 5: settings wired into live list + print views."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FE = ROOT / "Frontend" / "src"

LIST_WIRING = {
    "sales/invoices/page.tsx": "sales-invoice",
    "sales/receipts/page.tsx": "sales-receipt",
    "sales/customers/page.tsx": "customers",
    "purchases/bills/page.tsx": "supplier-bill",
    "purchases/payments/page.tsx": "supplier-payment",
    "inventory/products/page.tsx": "products",
}

PRINT_TEMPLATE_MARKERS = {
    "print/sales-invoice/[id]/page.tsx": "usePrintTemplate",
    "print/supplier-bill/[id]/page.tsx": "usePrintTemplate",
    "print/sales-receipt/[id]/page.tsx": "useVoucherPrintPage",
    "print/supplier-payment/[id]/page.tsx": "useVoucherPrintPage",
    "components/print/planning-document-print.tsx": "usePrintTemplate",
    "components/print/document-print.tsx": "resolvePrintTitle",
    "components/print/voucher-print.tsx": "resolvePrintTitle",
}

HOOKS = [
    "lib/hooks/use-configured-list-columns.ts",
    "lib/hooks/use-print-template.ts",
    "lib/grid/apply-listing-layout.ts",
]


def resolve_path(rel: str) -> Path:
    if rel.startswith("print/"):
        return FE / "app" / rel
    if rel.startswith("components/"):
        return FE / rel
    return FE / "app" / "(app)" / rel


def check_file(rel: str, needle: str, label: str) -> list[str]:
    path = resolve_path(rel)
    if not path.exists():
        return [f"MISSING {label}: {rel}"]
    text = path.read_text(encoding="utf-8")
    if needle not in text:
        return [f"FAIL {label}: {rel} missing {needle!r}"]
    return []


def main() -> int:
    errors: list[str] = []

    for rel, listing_id in LIST_WIRING.items():
        path = FE / "app" / "(app)" / rel
        text = path.read_text(encoding="utf-8")
        if "useConfiguredListColumns" not in text:
            errors.append(f"FAIL list: {rel} not wired")
        elif f'"{listing_id}"' not in text:
            errors.append(f"FAIL list: {rel} wrong listing id (expected {listing_id})")

    for rel, needle in PRINT_TEMPLATE_MARKERS.items():
        errors.extend(check_file(rel, needle, "print"))

    for rel in HOOKS:
        if not (FE / rel).exists():
            errors.append(f"MISSING hook: {rel}")

    if errors:
        print("Wave 5 connectivity: FAILED")
        for e in errors:
            print(f"  {e}")
        return 1

    print("Wave 5 connectivity: OK")
    print(f"  {len(LIST_WIRING)} list pages wired")
    print(f"  {len(PRINT_TEMPLATE_MARKERS)} print surfaces checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
