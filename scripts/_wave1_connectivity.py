#!/usr/bin/env python3
"""Verify Wave 1 routes, pages, APIs, and FA module manifest alignment."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_APP = ROOT / "Frontend/src/app/(app)"
TENANT_PY = ROOT / "Backend/src/app/api/routes/tenant.py"
NAV_TS = ROOT / "Frontend/src/config/navigation.ts"
CMD_TS = ROOT / "Frontend/src/config/command-registry.ts"
WAVE1_TS = ROOT / "Frontend/src/config/wave1-connections.ts"
MANIFEST_PY = ROOT / "scripts/fastaccounts_export/modules_manifest.py"

WAVE1 = [
    ("sales_all", "/sales/all", "/sales-activity", "GET"),
    ("purchases_all", "/purchases/all", "/purchases-activity", "GET"),
    ("bank_import_statement", "/bank/import-statement", "/bank-statement-import", "POST"),
    ("analytical_reports", "/reports/analytical", "/reports/definitions", "GET"),
]


def has_page(href: str) -> bool:
    path = href.strip("/")
    return (FRONTEND_APP / path / "page.tsx").is_file()


def main() -> int:
    errors: list[str] = []
    tenant = TENANT_PY.read_text(encoding="utf-8")

    for module_key, href, api_path, method in WAVE1:
        if module_key not in MANIFEST_PY.read_text(encoding="utf-8"):
            errors.append(f"modules_manifest missing ModuleDef key: {module_key}")
        if href not in NAV_TS.read_text(encoding="utf-8"):
            errors.append(f"navigation.ts missing href: {href}")
        if not has_page(href):
            errors.append(f"no page.tsx for {href}")
        route_pat = rf'@router\.{method.lower()}\("{re.escape(api_path)}"'
        if not re.search(route_pat, tenant):
            errors.append(f"tenant.py missing {method} {api_path}")
        if href not in CMD_TS.read_text(encoding="utf-8"):
            errors.append(f"command-registry.ts missing href: {href}")
        if href not in WAVE1_TS.read_text(encoding="utf-8"):
            errors.append(f"wave1-connections.ts missing href: {href}")

    if errors:
        print("Wave 1 connectivity FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("Wave 1 connectivity OK (4 modules, nav, pages, APIs, command palette, manifest)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
