#!/usr/bin/env python3
"""Verify settings-menu hrefs have pages and backend APIs where applicable."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_APP = ROOT / "Frontend/src/app/(app)"
SETTINGS_MENU = ROOT / "Frontend/src/config/settings-menu.ts"
TENANT_PY = ROOT / "Backend/src/app/api/routes/tenant.py"

PRINTING_API = "/print-templates"
CONTENT_API = "/content-settings/listings"
APP_SETTINGS_APIS = (
    "/application-settings/filters",
    "/application-settings/columns",
    "/application-settings/email",
    "/application-settings/dashboards",
    "/application-settings/op-methods",
    "/application-settings/missed-recurrence",
    "/sent-emails",
)


def extract_hrefs(text: str) -> set[str]:
    return set(re.findall(r'href:\s*"([^"]+)"', text))


def has_page(href: str) -> bool:
    if href.startswith("/settings/printing/"):
        return (FRONTEND_APP / "settings/printing/[code]/page.tsx").is_file()
    path = href.strip("/")
    return (FRONTEND_APP / path / "page.tsx").is_file()


def main() -> int:
    errors: list[str] = []
    menu = SETTINGS_MENU.read_text(encoding="utf-8")
    tenant = TENANT_PY.read_text(encoding="utf-8")
    hrefs = extract_hrefs(menu)

    for href in sorted(hrefs):
        if not has_page(href):
            errors.append(f"no page for {href}")

    for api in (PRINTING_API, CONTENT_API, *APP_SETTINGS_APIS):
        if api not in tenant:
            errors.append(f"tenant.py missing route containing {api}")

    if errors:
        print("Settings connectivity FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"Settings connectivity OK ({len(hrefs)} menu links, APIs present)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
