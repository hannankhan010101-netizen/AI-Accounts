"""Verify Wave 3: report catalog + generic runner wired end-to-end."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FE = ROOT / "Frontend" / "src"
BE = ROOT / "Backend" / "src" / "app"


def read(rel: str) -> str:
    return (FE / rel).read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []

    if "execute_report_sync" not in (BE / "api" / "routes" / "tenant.py").read_text(encoding="utf-8"):
        errors.append("Backend missing GET /reports/execute")

    tenant_ts = read("lib/api/tenant.ts")
    if "executeReport" not in tenant_ts:
        errors.append("Frontend missing reportsApi.executeReport")

    href_ts = read("lib/reports/report-id-href.ts")
    if "reportIdHref" not in href_ts or "/reports/run/" not in href_ts:
        errors.append("Frontend missing reportIdHref fallback runner")

    for page in [
        "app/(app)/reports/run/[reportId]/page.tsx",
        "app/(app)/reports/catalog/page.tsx",
    ]:
        if not (FE / page).exists():
            errors.append(f"Missing page: {page}")

    analytical = read("app/(app)/reports/analytical/page.tsx")
    if "UI pending" in analytical:
        errors.append("Analytical hub still shows UI pending stubs")
    if "reportIdHref" not in analytical:
        errors.append("Analytical hub not using reportIdHref")

    if errors:
        print("Wave 3 connectivity: FAILED")
        for e in errors:
            print(f"  {e}")
        return 1

    print("Wave 3 connectivity: OK")
    print("  GET /reports/execute + generic /reports/run/[id] + /reports/catalog")
    return 0


if __name__ == "__main__":
    sys.exit(main())
