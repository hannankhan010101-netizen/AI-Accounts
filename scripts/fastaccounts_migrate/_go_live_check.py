#!/usr/bin/env python3
"""Run go-live verification scripts (reconcile, TB, AR/AP) for migrated tenant."""
from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DIR))
from _tenant import tenant_id  # noqa: E402

REPO = DIR.parents[1]
PY = sys.executable
SIGNOFF = REPO / "Backend/docs/GO-LIVE-SIGNOFF-LATEST.md"
TENANT = tenant_id()

CHECKS = [
    ("preflight_deploy", DIR / "_preflight_deploy.py", True),
    ("reconcile", DIR / "_reconcile.py", True),
    ("trial_balance", DIR / "_tb_spot_check.py", True),
    ("migration_health", DIR / "_migration_health.py", False),
    ("report_spot_check", DIR / "_report_spot_check.py", False),
    ("integrations", DIR / "_integrations_readiness.py", False),
    ("ar_ap_aging", DIR / "_ar_ap_spot_check.py", False),
]


def run_script(label: str, path: Path, *, required: bool) -> tuple[str, int]:
    print(f"\n{'=' * 60}\n  {label} ({path.name})\n{'=' * 60}\n")
    proc = subprocess.run([PY, str(path)], cwd=str(REPO))
    ok = proc.returncode == 0
    status = "PASS" if ok else ("REVIEW" if not required else "FAIL")
    print(f"\n  [{label}] {status} (exit {proc.returncode})")
    return status, proc.returncode


def write_signoff(results: list[tuple[str, str, bool, int]]) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    required_ok = all(s == "PASS" for _, s, req, _ in results if req)
    lines = [
        "# Go-live verification (latest run)",
        "",
        f"**Generated:** {ts}  ",
        f"**Tenant:** `{TENANT}`  ",
        f"**Overall:** {'**GO** (preflight + reconcile + TB pass)' if required_ok else '**NO-GO** (fix required gates)'}",
        "",
        "| Check | Required | Result | Exit |",
        "|-------|----------|--------|------|",
    ]
    for label, status, required, code in results:
        lines.append(f"| {label} | {'yes' if required else 'no'} | {status} | {code} |")
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- AR/AP and party aging often **REVIEW** with summary GL migration.",
            "- ~47 draft SI / ~17 draft VI are expected; do not bulk-post on summary GL.",
            "- Nafy in-scope parity: see [NAFY-IN-SCOPE-SIGNOFF-LATEST.md](./NAFY-IN-SCOPE-SIGNOFF-LATEST.md).",
            "- Human UAT: [NAFY-UAT-CHECKLIST.md](./NAFY-UAT-CHECKLIST.md).",
            "- Re-run: `python scripts/fastaccounts_migrate/_go_live_check.py`",
            "- Full runbook: [GO-LIVE-RUNBOOK.md](./GO-LIVE-RUNBOOK.md)",
            "",
        ]
    )
    SIGNOFF.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n  Sign-off written: {SIGNOFF.relative_to(REPO)}")


def main() -> int:
    print("=== AI-Accounts go-live check (Nafy-Pharma) ===")
    results: list[tuple[str, str, bool, int]] = []
    all_required_ok = True
    for label, script, required in CHECKS:
        status, code = run_script(label, script, required=required)
        results.append((label, status, required, code))
        if required and status != "PASS":
            all_required_ok = False

    write_signoff(results)

    print("\n=== Go-live summary ===")
    if all_required_ok:
        print("  Required checks: PASS (preflight + reconcile + trial balance)")
        print("  Migration health / AR/AP may show REVIEW - see script output.")
        print("  Draft SI/VI: use approve or _bulk_post_drafts.py only when open-item GL is intended.")
        return 0
    print("  Required checks: FAIL - fix reconcile or trial balance before go-live.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
