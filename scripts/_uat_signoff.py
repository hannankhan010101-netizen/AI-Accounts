#!/usr/bin/env python3
"""Load Nafy UAT sign-off JSON and write NAFY-UAT-SIGNOFF-LATEST.md.

Usage:
  python scripts/_uat_signoff.py
  python scripts/_uat_signoff.py --record --business-owner "..." --finance "..." --technical-lead "..." --result PASS
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAFY_UAT_CONFIG = ROOT / "Backend/config/nafy_uat_signoff.json"
NAFY_UAT_SIGNOFF = ROOT / "Backend/docs/NAFY-UAT-SIGNOFF-LATEST.md"
NAFY_EXCLUSIONS = ROOT / "Backend/config/nafy_parity_exclusions.json"

VALID_RESULTS = frozenset({"PASS", "PASS_WITH_WAIVERS", "FAIL"})


def load_uat_signoff() -> dict | None:
    if not NAFY_UAT_CONFIG.is_file():
        return None
    payload = json.loads(NAFY_UAT_CONFIG.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else None


def uat_passed() -> bool:
    data = load_uat_signoff()
    if not data:
        return False
    result = str(data.get("result") or "").strip().upper()
    return result in ("PASS", "PASS_WITH_WAIVERS")


def uat_status_line() -> tuple[str, bool]:
    data = load_uat_signoff()
    if not data:
        return (
            "**Pending** — complete [NAFY-UAT-CHECKLIST.md](./NAFY-UAT-CHECKLIST.md)",
            False,
        )
    result = str(data.get("result") or "").strip().upper()
    if result == "PASS":
        return "**PASS**", True
    if result == "PASS_WITH_WAIVERS":
        return "**PASS with waivers**", True
    if result == "FAIL":
        return "**FAIL**", False
    return f"**Unknown result** ({result})", False


def _tenant_meta() -> tuple[str, str]:
    tenant_id = "cmpfm1nst0001lhq3rz09938z"
    tenant_label = "Nafy-Pharma"
    if NAFY_EXCLUSIONS.is_file():
        cfg = json.loads(NAFY_EXCLUSIONS.read_text(encoding="utf-8"))
        tenant_id = str(cfg.get("tenantId") or tenant_id)
        tenant_label = str(cfg.get("tenantLabel") or tenant_label)
    return tenant_id, tenant_label


def write_uat_signoff_doc(*, ts: str | None = None) -> None:
    ts = ts or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    tenant_id, tenant_label = _tenant_meta()
    data = load_uat_signoff()

    if not data:
        lines = [
            "# Nafy UAT sign-off (latest)",
            "",
            f"**Generated:** {ts}  ",
            f"**Tenant:** `{tenant_id}` ({tenant_label})  ",
            "**Status:** **Pending** — no recorded sign-off yet.",
            "",
            "## How to record",
            "",
            "1. Complete every row in [NAFY-UAT-CHECKLIST.md](./NAFY-UAT-CHECKLIST.md).",
            "2. Run:",
            "",
            "```powershell",
            ".\\scripts\\record-uat-signoff.ps1 `",
            '  -BusinessOwner "..." -Finance "..." -TechnicalLead "..." `',
            "  -Result PASS",
            "```",
            "",
            "Template: `Backend/config/nafy_uat_signoff.json.example`",
            "",
        ]
        NAFY_UAT_SIGNOFF.write_text("\n".join(lines), encoding="utf-8")
        return

    result = str(data.get("result") or "PASS").strip().upper()
    recorded_at = str(data.get("recordedAt") or data.get("date") or ts)
    signers = data.get("signers") or {}
    waivers = str(data.get("waivers") or "").strip()
    notes = str(data.get("notes") or "").strip()

    status_display = {
        "PASS": "**PASS**",
        "PASS_WITH_WAIVERS": "**PASS with waivers**",
        "FAIL": "**FAIL**",
    }.get(result, f"**{result}**")

    lines = [
        "# Nafy UAT sign-off (latest)",
        "",
        f"**Generated:** {ts}  ",
        f"**Recorded:** {recorded_at}  ",
        f"**Tenant:** `{tenant_id}` ({tenant_label})  ",
        f"**Overall result:** {status_display}",
        "",
        "## Signatories",
        "",
        "| Role | Name |",
        "|------|------|",
        f"| Business owner | {signers.get('businessOwner', '')} |",
        f"| Finance / accounts | {signers.get('finance', '')} |",
        f"| Technical lead | {signers.get('technicalLead', '')} |",
        "",
    ]
    if waivers:
        lines.extend(["## Waivers", "", waivers, ""])
    if notes:
        lines.extend(["## Notes", "", notes, ""])
    lines.extend(
        [
            "Checklist: [NAFY-UAT-CHECKLIST.md](./NAFY-UAT-CHECKLIST.md)",
            "",
            "Regenerate: `python scripts/_uat_signoff.py`",
            "",
        ]
    )
    NAFY_UAT_SIGNOFF.write_text("\n".join(lines), encoding="utf-8")


def save_uat_signoff(payload: dict) -> None:
    result = str(payload.get("result") or "").strip().upper()
    if result not in VALID_RESULTS:
        raise ValueError(f"result must be one of {sorted(VALID_RESULTS)}")
    payload["result"] = result
    if "recordedAt" not in payload:
        payload["recordedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    NAFY_UAT_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    NAFY_UAT_CONFIG.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Nafy UAT sign-off artifact")
    parser.add_argument("--record", action="store_true", help="Write sign-off JSON from CLI args")
    parser.add_argument("--business-owner", default="")
    parser.add_argument("--finance", default="")
    parser.add_argument("--technical-lead", default="")
    parser.add_argument(
        "--result",
        default="PASS",
        choices=sorted(VALID_RESULTS),
        help="Overall UAT result",
    )
    parser.add_argument("--waivers", default="")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    if args.record:
        if not args.business_owner or not args.finance or not args.technical_lead:
            print(
                "When --record is set, --business-owner, --finance, and --technical-lead are required.",
                file=sys.stderr,
            )
            return 1
        save_uat_signoff(
            {
                "result": args.result,
                "signers": {
                    "businessOwner": args.business_owner,
                    "finance": args.finance,
                    "technicalLead": args.technical_lead,
                },
                "waivers": args.waivers,
                "notes": args.notes,
            }
        )

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    write_uat_signoff_doc(ts=ts)
    print(f"Wrote {NAFY_UAT_SIGNOFF.relative_to(ROOT)}")
    status, ok = uat_status_line()
    print(f"  uat: {status.replace('**', '')}")
    if args.record and args.result == "FAIL":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
