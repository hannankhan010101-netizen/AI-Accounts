#!/usr/bin/env python3
"""Aggregate Nafy release gates into NAFY-RELEASE-READINESS-LATEST.md.

Usage:
  python scripts/_release_readiness.py
  python scripts/_release_readiness.py --strict-predeploy   # exit 1 if pre-deploy gates fail
  python scripts/_release_readiness.py --strict-business    # exit 1 unless UAT + all pre-deploy pass
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "Backend/docs/FA-FEATURE-MATRIX.csv"
GO_LIVE_SIGNOFF = ROOT / "Backend/docs/GO-LIVE-SIGNOFF-LATEST.md"
NAFY_EXCLUSIONS = ROOT / "Backend/config/nafy_parity_exclusions.json"
PROD_HANDOFF = ROOT / "Backend/config/nafy_prod_handoff.json"
OUT = ROOT / "Backend/docs/NAFY-RELEASE-READINESS-LATEST.md"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _status_bucket(raw: str) -> str:
    s = (raw or "").strip()
    if s.startswith("✅"):
        return "done"
    if s.startswith("⚠️"):
        return "partial"
    if s.startswith("❌"):
        return "missing"
    return "other"


def _nafy_scope_done() -> tuple[bool, str]:
    if not MATRIX.is_file():
        return False, "matrix missing — run _generate_feature_matrix.py"
    excluded: set[str] = set()
    if NAFY_EXCLUSIONS.is_file():
        payload = json.loads(NAFY_EXCLUSIONS.read_text(encoding="utf-8"))
        excluded = {str(x).strip() for x in payload.get("excludedFeatures") or [] if str(x).strip()}
    with MATRIX.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    in_scope = [r for r in rows if r.get("fa_feature", "").strip() not in excluded]
    done = sum(1 for r in in_scope if _status_bucket(r.get("status", "")) == "done")
    total = len(in_scope)
    if done == total and total > 0:
        return True, f"{done}/{total} in-scope rows ✅"
    return False, f"{done}/{total} in-scope (partial/missing remain)"


def _go_live_ok() -> tuple[bool, str]:
    if not GO_LIVE_SIGNOFF.is_file():
        return False, "run go-live.ps1 or _go_live_check.py"
    text = GO_LIVE_SIGNOFF.read_text(encoding="utf-8")
    if "**NO-GO**" in text:
        return False, "NO-GO — see GO-LIVE-SIGNOFF-LATEST.md"
    if "**GO**" not in text:
        return False, "review GO-LIVE-SIGNOFF-LATEST.md"
    spot = "report_spot_check | no | PASS" in text or "report_spot_check | yes | PASS" in text
    if not spot:
        return True, "GO (report spot-check not PASS — review sign-off)"
    return True, "GO + report spot-check PASS"


def _uat_ok() -> tuple[bool, str]:
    uat = _load_module("uat_signoff", ROOT / "scripts/_uat_signoff.py")
    line, ok = uat.uat_status_line()
    return ok, line.replace("**", "")


def _prod_smoke_ok() -> tuple[bool, str]:
    if not PROD_HANDOFF.is_file():
        return False, "not run — use nafy-prod-handoff.ps1 after deploy"
    payload = json.loads(PROD_HANDOFF.read_text(encoding="utf-8"))
    result = str(payload.get("result") or "").strip().upper()
    api = str(payload.get("apiUrl") or "").strip()
    when = str(payload.get("recordedAt") or payload.get("lastSmokeAt") or "").strip()
    if result == "PASS" and api:
        suffix = f" ({when})" if when else ""
        return True, f"PASS — {api}{suffix}"
    if result == "FAIL":
        return False, f"FAIL — {api or 'see nafy_prod_handoff.json'}"
    return False, "not recorded"


def _deploy_ready(predeploy_ok: bool, smoke_ok: bool) -> tuple[bool, str]:
    if not predeploy_ok:
        return False, "fix pre-deploy gates first"
    if smoke_ok:
        return True, "deploy smoke recorded"
    return True, "ready to deploy (run prod handoff after Railway/Vercel)"


def _business_ready(*, scope_ok: bool, go_ok: bool, uat_ok: bool, smoke_ok: bool) -> tuple[bool, str]:
    missing: list[str] = []
    if not scope_ok:
        missing.append("in-scope parity")
    if not go_ok:
        missing.append("data go-live")
    if not smoke_ok:
        missing.append("prod deploy smoke")
    if not uat_ok:
        missing.append("human UAT")
    if missing:
        return False, "still needed: " + ", ".join(missing)
    return True, "all business gates satisfied"


def write_readiness(*, ts: str | None = None) -> dict[str, tuple[bool, str]]:
    ts = ts or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    scope_ok, scope_detail = _nafy_scope_done()
    go_ok, go_detail = _go_live_ok()
    uat_ok_flag, uat_detail = _uat_ok()
    smoke_ok, smoke_detail = _prod_smoke_ok()
    predeploy_ok = scope_ok and go_ok
    deploy_ok, deploy_detail = _deploy_ready(predeploy_ok, smoke_ok)
    business_ok, business_detail = _business_ready(
        scope_ok=scope_ok,
        go_ok=go_ok,
        uat_ok=uat_ok_flag,
        smoke_ok=smoke_ok,
    )

    def row(label: str, ok: bool, detail: str, phase: str) -> str:
        status = "**PASS**" if ok else "**Pending**"
        return f"| {label} | {phase} | {status} | {detail} |"

    lines = [
        "# Nafy release readiness (latest)",
        "",
        f"**Generated:** {ts}  ",
        f"**Pre-deploy ready:** {'**YES**' if predeploy_ok else '**NO**'}  ",
        f"**Deploy smoke:** {'**PASS**' if smoke_ok else '**Pending**'}  ",
        f"**Business go-live:** {'**READY**' if business_ok else '**NOT READY**'} — {business_detail}",
        "",
        "## Gates",
        "",
        "| Gate | Phase | Status | Detail |",
        "|------|-------|--------|--------|",
        row("In-scope FA parity", scope_ok, scope_detail, "pre-deploy"),
        row("Migration / data go-live", go_ok, go_detail, "pre-deploy"),
        row("Production deploy smoke", smoke_ok, smoke_detail, "deploy"),
        row("Human UAT", uat_ok_flag, uat_detail, "post-deploy"),
        "",
        "## Commands",
        "",
        "```powershell",
        "# Pre-deploy (local / prod DB in Backend/.env)",
        ".\\scripts\\release-check.ps1 -SkipEnvStrict",
        "",
        "# After Railway + Vercel deploy",
        ".\\scripts\\nafy-prod-handoff.ps1 -ApiUrl https://<api> -FrontendUrl https://<app>",
        "",
        "# After UAT checklist",
        ".\\scripts\\record-uat-signoff.ps1 -BusinessOwner ... -Finance ... -TechnicalLead ... -Result PASS",
        "",
        "# Full business gate",
        "python scripts/_parity_progress.py --strict-nafy-release",
        "```",
        "",
        "Artifacts: [GO-LIVE-SIGNOFF-LATEST.md](./GO-LIVE-SIGNOFF-LATEST.md) · "
        "[NAFY-IN-SCOPE-SIGNOFF-LATEST.md](./NAFY-IN-SCOPE-SIGNOFF-LATEST.md) · "
        "[NAFY-UAT-SIGNOFF-LATEST.md](./NAFY-UAT-SIGNOFF-LATEST.md)",
        "",
    ]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    return {
        "scope": (scope_ok, scope_detail),
        "go_live": (go_ok, go_detail),
        "smoke": (smoke_ok, smoke_detail),
        "uat": (uat_ok_flag, uat_detail),
        "predeploy": (predeploy_ok, ""),
        "business": (business_ok, business_detail),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Nafy release readiness dashboard")
    parser.add_argument(
        "--strict-predeploy",
        action="store_true",
        help="Exit 1 unless in-scope parity and data go-live are pass",
    )
    parser.add_argument(
        "--strict-business",
        action="store_true",
        help="Exit 1 unless business go-live ready (includes UAT + prod smoke)",
    )
    args = parser.parse_args()

    gates = write_readiness()
    print(f"Wrote {OUT.relative_to(ROOT)}")
    print(f"  pre-deploy: {'READY' if gates['predeploy'][0] else 'NOT READY'}")
    print(f"  business:   {gates['business'][1]}")

    if args.strict_predeploy and not gates["predeploy"][0]:
        return 1
    if args.strict_business and not gates["business"][0]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
