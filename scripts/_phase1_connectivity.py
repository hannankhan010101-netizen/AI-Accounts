#!/usr/bin/env python3
"""Phase 1 — assembly, FX, projects, locations routes and APIs."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_APP = ROOT / "Frontend/src/app/(app)"
TENANT_PY = ROOT / "Backend/src/app/api/routes/tenant.py"
NAV_TS = ROOT / "Frontend/src/config/navigation.ts"
SETTINGS_MENU = ROOT / "Frontend/src/config/settings-menu.ts"
TENANT_TS = ROOT / "Frontend/src/lib/api/tenant.ts"

PHASE1 = [
    ("/inventory/assembly/templates", "/assembly/templates", "listTemplates"),
    ("/inventory/assembly/jobs", "/assembly/jobs", "listJobs"),
    ("/bank/fx-revaluation", "/bank/fx-revaluations", "fxRevaluationApi"),
    ("/settings/projects", "/projects", "projectsApi"),
    ("/settings/locations", "/locations", "locationsApi"),
]


def has_page(href: str) -> bool:
    path = href.strip("/")
    return (FRONTEND_APP / path / "page.tsx").is_file()


def main() -> int:
    errors: list[str] = []
    tenant = TENANT_PY.read_text(encoding="utf-8")
    nav = NAV_TS.read_text(encoding="utf-8")
    settings = SETTINGS_MENU.read_text(encoding="utf-8")
    client = TENANT_TS.read_text(encoding="utf-8")

    for href, api_path, client_sym in PHASE1:
        if href not in nav and href not in settings:
            errors.append(f"missing nav/settings href: {href}")
        if not has_page(href):
            errors.append(f"no page.tsx for {href}")
        if api_path not in tenant:
            errors.append(f"tenant.py missing {api_path}")
        if client_sym not in client:
            errors.append(f"tenant.ts missing {client_sym}")

    if errors:
        print("Phase 1 connectivity FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("Phase 1 connectivity OK (assembly, FX, projects, locations)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
