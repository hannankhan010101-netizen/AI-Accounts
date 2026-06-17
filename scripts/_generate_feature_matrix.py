#!/usr/bin/env python3
"""Generate Backend/docs/FA-FEATURE-MATRIX.csv from FA-FULL-PARITY-IMPLEMENTATION-PLAN.md §3."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "Backend/docs/FA-FULL-PARITY-IMPLEMENTATION-PLAN.md"
OUT = ROOT / "Backend/docs/FA-FEATURE-MATRIX.csv"

SECTION_RE = re.compile(r"^### (§.+)$")
ROW_RE = re.compile(r"^\| (.+?) \| ([✅⚠️❌][^|]*) \| ([^|]+) \|$")


def main() -> None:
    text = PLAN.read_text(encoding="utf-8")
    section = ""
    rows: list[dict[str, str]] = []

    for line in text.splitlines():
        m_sec = SECTION_RE.match(line.strip())
        if m_sec:
            section = m_sec.group(1).strip()
            continue
        m_row = ROW_RE.match(line.strip())
        if not m_row or m_row.group(1).lower() == "feature":
            continue
        feature, status, phase = (c.strip() for c in m_row.groups())
        rows.append(
            {
                "fa_section": section,
                "fa_feature": feature,
                "fa_ref": section,
                "ai_route": "",
                "ai_api": "",
                "status": status,
                "phase": phase,
                "owner": "",
                "pr_link": "",
            }
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "fa_section",
        "fa_feature",
        "fa_ref",
        "ai_route",
        "ai_api",
        "status",
        "phase",
        "owner",
        "pr_link",
    ]
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    done = sum(1 for r in rows if r["status"].startswith("✅"))
    partial = sum(1 for r in rows if r["status"].startswith("⚠️"))
    missing = sum(1 for r in rows if r["status"].startswith("❌"))
    print(f"Wrote {len(rows)} rows to {OUT.relative_to(ROOT)}")
    print(f"  done={done}  partial={partial}  missing={missing}")
    try:
        import subprocess

        subprocess.run([sys.executable, str(ROOT / "scripts/_parity_progress.py")], check=False)
    except OSError:
        pass


if __name__ == "__main__":
    main()
