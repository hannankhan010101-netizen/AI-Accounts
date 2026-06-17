#!/usr/bin/env python3
"""Merge multiple FastAccounts export JSON files into one consolidated file."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "output"


def merge_exports(paths: list[Path], out_path: Path) -> dict:
    merged_modules: dict = {}
    account: dict = {}
    base_url = ""
    all_errors: list[dict] = []

    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        account = data.get("account") or account
        base_url = data.get("baseUrl") or base_url
        all_errors.extend(data.get("errors") or [])
        for key, mod in (data.get("modules") or {}).items():
            if key == "discovered_sidebar_links":
                merged_modules[key] = mod
                continue
            existing = merged_modules.get(key)
            if existing is None or mod.get("recordCount", 0) >= existing.get("recordCount", 0):
                merged_modules[key] = mod

    # Deduplicate errors by module+message
    seen_errors: set[str] = set()
    unique_errors: list[dict] = []
    for err in all_errors:
        sig = f"{err.get('module')}:{err.get('message')}"
        if sig not in seen_errors:
            seen_errors.add(sig)
            unique_errors.append(err)

    total_records = sum(
        m.get("recordCount", 0)
        for k, m in merged_modules.items()
        if k != "discovered_sidebar_links"
    )

    return {
        "exportedAt": datetime.now(timezone.utc).isoformat(),
        "mergedFrom": [str(p.name) for p in paths],
        "account": account,
        "baseUrl": base_url,
        "totalModules": len(merged_modules),
        "totalRecords": total_records,
        "modules": merged_modules,
        "errors": unique_errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge FastAccounts export JSON files")
    parser.add_argument(
        "files",
        nargs="*",
        help="Export JSON files to merge (default: all fastaccounts_export_*.json in output/)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=str(OUTPUT_DIR / "fastaccounts_export_complete.json"),
        help="Output merged JSON path",
    )
    args = parser.parse_args()

    if args.files:
        paths = [Path(f) for f in args.files]
    else:
        paths = sorted(OUTPUT_DIR.glob("fastaccounts_export_*.json"))
        paths = [p for p in paths if "complete" not in p.name]

    if not paths:
        raise SystemExit("No export files found to merge.")

    result = merge_exports(paths, Path(args.output))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    summary = {
        "mergedAt": result["exportedAt"],
        "sourceFiles": result["mergedFrom"],
        "totalModules": result["totalModules"],
        "totalRecords": result["totalRecords"],
        "modules": [
            {
                "key": k,
                "label": v.get("label", k),
                "recordCount": v.get("recordCount", 0),
                "status": "ok" if v.get("recordCount", 0) > 0 or not v.get("errors") else "empty",
            }
            for k, v in result["modules"].items()
        ],
        "errors": result["errors"],
    }
    summary_path = out.parent / "export_summary_complete.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Merged {len(paths)} files -> {out}")
    print(f"Modules: {result['totalModules']}, Total records: {result['totalRecords']}")
    print(f"Summary -> {summary_path}")


if __name__ == "__main__":
    main()
