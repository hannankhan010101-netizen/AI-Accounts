"""Verify Wave 4: header chrome wired end-to-end."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FE = ROOT / "Frontend" / "src"
BE = ROOT / "Backend" / "src" / "app"


def main() -> int:
    errors: list[str] = []

    auth_py = (BE / "api" / "routes" / "auth.py").read_text(encoding="utf-8")
    tenant_py = (BE / "api" / "routes" / "tenant.py").read_text(encoding="utf-8")
    top_bar = (FE / "components" / "app" / "top-bar.tsx").read_text(encoding="utf-8")

    for needle, msg in [
        ('@router.get("/me"', "GET /auth/me"),
        ('@router.post("/change-password"', "POST /auth/change-password"),
        ('@router.get("/my-tasks"', "GET /my-tasks"),
    ]:
        hay = auth_py if "auth" in msg else tenant_py
        if needle not in hay:
            errors.append(f"Backend missing {msg}")

    pages = [
        "app/(app)/profile/page.tsx",
        "app/(app)/profile/change-password/page.tsx",
        "app/(app)/my-tasks/page.tsx",
        "app/(app)/support/page.tsx",
        "components/app/user-menu.tsx",
    ]
    for page in pages:
        if not (FE / page).exists():
            errors.append(f"Missing {page}")

    for needle in ["/my-tasks", "/support", "UserMenu", "activity-log"]:
        if needle not in top_bar:
            errors.append(f"TopBar missing {needle}")

    if "<button\n                </div>" in top_bar:
        errors.append("TopBar mobile menu JSX is broken")

    if errors:
        print("Wave 4 connectivity: FAILED")
        for e in errors:
            print(f"  {e}")
        return 1

    print("Wave 4 connectivity: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
