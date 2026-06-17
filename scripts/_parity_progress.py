#!/usr/bin/env python3
"""Summarize FA parity from FA-FEATURE-MATRIX.csv and write PARITY-PROGRESS-LATEST.md.

Exit 0 always for reporting; use --strict to fail when any row is not full done (future full-parity gate).

Usage:
  python scripts/_parity_progress.py
  python scripts/_parity_progress.py --strict
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "Backend/docs/FA-FEATURE-MATRIX.csv"
OUT = ROOT / "Backend/docs/PARITY-PROGRESS-LATEST.md"
SIGNOFF = ROOT / "Backend/docs/GO-LIVE-SIGNOFF-LATEST.md"
NAFY_EXCLUSIONS = ROOT / "Backend/config/nafy_parity_exclusions.json"
NAFY_SIGNOFF = ROOT / "Backend/docs/NAFY-IN-SCOPE-SIGNOFF-LATEST.md"
NAFY_UAT_SIGNOFF = ROOT / "Backend/docs/NAFY-UAT-SIGNOFF-LATEST.md"


def _uat_module():
    spec = importlib.util.spec_from_file_location(
        "uat_signoff", ROOT / "scripts/_uat_signoff.py"
    )
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


def _read_rows() -> list[dict[str, str]]:
    if not MATRIX.is_file():
        print(f"Missing {MATRIX.relative_to(ROOT)} — run scripts/_generate_feature_matrix.py", file=sys.stderr)
        sys.exit(1)
    with MATRIX.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _load_nafy_exclusions() -> frozenset[str]:
    if not NAFY_EXCLUSIONS.is_file():
        return frozenset()
    import json

    payload = json.loads(NAFY_EXCLUSIONS.read_text(encoding="utf-8"))
    items = payload.get("excludedFeatures") or []
    return frozenset(str(x).strip() for x in items if str(x).strip())


def _load_nafy_config() -> dict:
    if not NAFY_EXCLUSIONS.is_file():
        return {}
    import json

    payload = json.loads(NAFY_EXCLUSIONS.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _write_nafy_signoff(
    *,
    ts: str,
    nafy_total: int,
    nafy_done: int,
    nafy_scope_done: bool,
    go_live: str,
    excluded: frozenset[str],
    uat_line: str,
) -> None:
    cfg = _load_nafy_config()
    tenant_id = str(cfg.get("tenantId") or "cmpfm1nst0001lhq3rz09938z")
    tenant_label = str(cfg.get("tenantLabel") or "Nafy-Pharma")
    go_ok = "GO" in go_live and "NO-GO" not in go_live

    lines = [
        "# Nafy in-scope parity sign-off (latest)",
        "",
        f"**Generated:** {ts}  ",
        f"**Tenant:** `{tenant_id}` ({tenant_label})  ",
        f"**In-scope matrix:** {nafy_done}/{nafy_total} ✅ — "
        f"{'**DONE**' if nafy_scope_done else '**NOT DONE**'}",
        f"**Data go-live gate:** {go_live}",
        "",
        "## Excluded features (not licensed for this tenant)",
        "",
    ]
    for name in sorted(excluded):
        lines.append(f"- {name}")
    lines.extend(
        [
            "",
            "## Release gates",
            "",
            "| Gate | Status |",
            "|------|--------|",
            f"| In-scope FA parity ({nafy_done}/{nafy_total}) | "
            f"{'**DONE**' if nafy_scope_done else '**NOT DONE**'} |",
            f"| Migration / TB go-live (`_go_live_check.py`) | "
            f"{'**GO**' if go_ok else 'review GO-LIVE-SIGNOFF-LATEST.md'} |",
            f"| Human UAT | {uat_line} |",
            "| Prod integrations (FBR/email) | Configure on deploy — see Integration settings |",
            "",
            "## Next steps",
            "",
            "1. Deploy production (see [DEPLOY-QUICKSTART.md](./DEPLOY-QUICKSTART.md)).",
            "2. Run `scripts/nafy-prod-handoff.ps1 -ApiUrl ... -FrontendUrl ... -RunGoLive`.",
            "3. Complete [NAFY-UAT-CHECKLIST.md](./NAFY-UAT-CHECKLIST.md), then "
            "`scripts/record-uat-signoff.ps1` (see [NAFY-UAT-SIGNOFF-LATEST.md](./NAFY-UAT-SIGNOFF-LATEST.md)).",
            "",
            "Regenerate: `python scripts/_generate_feature_matrix.py`",
            "",
        ]
    )
    NAFY_SIGNOFF.write_text("\n".join(lines), encoding="utf-8")


def _go_live_line() -> str:
    if not SIGNOFF.is_file():
        return "unknown (run go-live.ps1)"
    text = SIGNOFF.read_text(encoding="utf-8")
    if "**GO**" in text and "NO-GO" not in text.split("Overall:")[0]:
        return "**GO** (see GO-LIVE-SIGNOFF-LATEST.md)"
    if "NO-GO" in text:
        return "**NO-GO**"
    return "review sign-off file"


def main() -> int:
    parser = argparse.ArgumentParser(description="FA parity progress report")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 unless every matrix row is full done (no partial/missing)",
    )
    parser.add_argument(
        "--strict-nafy",
        action="store_true",
        help="Exit 1 unless Nafy in-scope rows are all full done",
    )
    parser.add_argument(
        "--strict-nafy-release",
        action="store_true",
        help="Exit 1 unless in-scope parity, go-live GO, and UAT PASS/PASS_WITH_WAIVERS",
    )
    args = parser.parse_args()

    rows = _read_rows()
    nafy_excluded = _load_nafy_exclusions()
    in_scope_rows = [
        r for r in rows if r.get("fa_feature", "").strip() not in nafy_excluded
    ]
    buckets = Counter(_status_bucket(r.get("status", "")) for r in rows)
    nafy_buckets = Counter(_status_bucket(r.get("status", "")) for r in in_scope_rows)
    total = len(rows)
    done = buckets.get("done", 0)
    partial = buckets.get("partial", 0)
    missing = buckets.get("missing", 0)
    pct = round(100.0 * done / total, 1) if total else 0.0

    nafy_total = len(in_scope_rows)
    nafy_done = nafy_buckets.get("done", 0)
    nafy_partial = nafy_buckets.get("partial", 0)
    nafy_missing = nafy_buckets.get("missing", 0)
    nafy_pct = round(100.0 * nafy_done / nafy_total, 1) if nafy_total else 0.0
    nafy_scope_done = nafy_partial == 0 and nafy_missing == 0 and nafy_total > 0

    full_parity_done = partial == 0 and missing == 0 and total > 0
    go_live = _go_live_line()
    go_ok = "GO" in go_live and "NO-GO" not in go_live

    uat = _uat_module()
    uat.write_uat_signoff_doc()
    uat_line, uat_ok = uat.uat_status_line()

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    by_section: Counter[str] = Counter()
    for row in rows:
        if _status_bucket(row.get("status", "")) != "done":
            by_section[row.get("fa_section", "?")] += 1

    lines = [
        "# Parity progress (latest)",
        "",
        f"**Generated:** {ts}  ",
        f"**Source:** `{MATRIX.relative_to(ROOT).as_posix()}` ({total} rows)",
        "",
        "## Signals",
        "",
        "| Gate | Status |",
        "|------|--------|",
        f"| Nafy **go-live** | {go_live} |",
        f"| **Nafy in-scope parity** | {'**DONE**' if nafy_scope_done else '**NOT DONE**'} |",
        f"| **Full FA catalog parity** | {'**DONE**' if full_parity_done else '**NOT DONE**'} |",
        "",
        "## Matrix counts",
        "",
        f"| Done | Partial | Missing | Full parity % |",
        f"|------|---------|---------|---------------|",
        f"| {done} | {partial} | {missing} | {pct}% |",
        "",
        "## Nafy in-scope parity (pharmacy tenant)",
        "",
        f"Excludes **{len(nafy_excluded)}** licensed add-on rows listed in "
        f"`Backend/config/nafy_parity_exclusions.json`.",
        "",
        f"| In-scope rows | Done | Partial | Missing | Nafy scope % |",
        f"|---------------|------|---------|---------|--------------|",
        f"| {nafy_total} | {nafy_done} | {nafy_partial} | {nafy_missing} | {nafy_pct}% |",
        "",
        f"| **Nafy in-scope parity** | {'**DONE**' if nafy_scope_done else '**NOT DONE**'} |",
        "",
        "## Nafy release exit criteria",
        "",
        f"- [{'x' if nafy_scope_done else ' '}] In-scope matrix: {nafy_done}/{nafy_total} done "
        f"(see [NAFY-IN-SCOPE-SIGNOFF-LATEST.md](./NAFY-IN-SCOPE-SIGNOFF-LATEST.md))",
        f"- [{'x' if go_ok else ' '}] `_go_live_check.py` required gates PASS",
        "- [ ] Production deploy smoke (`nafy-prod-handoff.ps1`)",
        f"- [{'x' if uat_ok else ' '}] Human UAT recorded "
        f"([NAFY-UAT-CHECKLIST.md](./NAFY-UAT-CHECKLIST.md) · "
        f"[NAFY-UAT-SIGNOFF-LATEST.md](./NAFY-UAT-SIGNOFF-LATEST.md))",
        "- [ ] Production Brevo/FBR env configured if licensed",
        "",
        "## Full catalog parity exit criteria (all 115 FA rows)",
        "",
        f"- [{'x' if full_parity_done else ' '}] `FA-FEATURE-MATRIX.csv`: zero partial/missing",
        "- [ ] Licensed add-ons implemented or permanently N/A",
        "- [ ] Authenticated Playwright parity in CI (`PLAYWRIGHT_AUTH_READY=1`)",
        "",
    ]

    if not full_parity_done and by_section:
        lines.extend(["## Open rows by FA section (not full done)", ""])
        for section, count in sorted(by_section.items(), key=lambda x: (-x[1], x[0])):
            lines.append(f"- {section}: {count}")
        lines.append("")

    lines.extend(
        [
            "## Regenerate",
            "",
            "```powershell",
            "python scripts/_generate_feature_matrix.py",
            "python scripts/_parity_progress.py",
            "```",
            "",
            "Tracker: [AI-ACCOUNTS-PARITY-STATUS.md](./AI-ACCOUNTS-PARITY-STATUS.md)",
            "",
        ]
    )

    OUT.write_text("\n".join(lines), encoding="utf-8")
    _write_nafy_signoff(
        ts=ts,
        nafy_total=nafy_total,
        nafy_done=nafy_done,
        nafy_scope_done=nafy_scope_done,
        go_live=go_live,
        excluded=nafy_excluded,
        uat_line=uat_line,
    )

    print(f"Wrote {OUT.relative_to(ROOT)}")
    print(f"Wrote {NAFY_SIGNOFF.relative_to(ROOT)}")
    print(f"Wrote {NAFY_UAT_SIGNOFF.relative_to(ROOT)}")

    import subprocess

    subprocess.run(
        [sys.executable, str(ROOT / "scripts/_release_readiness.py")],
        check=False,
    )

    print(f"  go-live: {go_live.replace('**', '')}")
    print(f"  uat: {uat_line.replace('**', '')}")
    print(f"  full parity: {'DONE' if full_parity_done else 'NOT DONE'}")
    print(f"  matrix: done={done} partial={partial} missing={missing} ({pct}%)")
    print(
        f"  nafy scope: done={nafy_done} partial={nafy_partial} missing={nafy_missing} ({nafy_pct}%)"
    )

    if args.strict and not full_parity_done:
        return 1
    if args.strict_nafy and not nafy_scope_done:
        return 1
    if args.strict_nafy_release and not (nafy_scope_done and go_ok and uat_ok):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
