#!/usr/bin/env python3
"""Build a human-labeled, records-only export from fastaccounts_export_complete.json."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from modules_manifest import ALL_MODULES

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "output"

# Known FastAccounts column -> display label overrides.
FIELD_LABELS: dict[str, str] = {
    "entityId": "ID",
    "BusinessName": "Business Name",
    "AccountNo": "Account No",
    "DisplayName": "Contact Name",
    "PartyBalance": "Balance",
    "InvoiceDate": "Invoice Date",
    "DocNo": "Document No",
    "FxTotal": "Total",
    "InvoiceIDLink": "Invoice No",
    "ProductName": "Product Name",
    "CategoryName": "Category",
    "SalePrice": "Sale Price",
    "LowStockLevel": "Low Stock Level",
    "cqty": "Quantity",
    "VoucherNo": "Voucher No",
    "PaymentDate": "Payment Date",
    "BankName": "Bank Name",
    "formFields": "Form Fields",
}

CATEGORY_LABELS: dict[str, str] = {
    "overview": "Overview",
    "bank": "Bank",
    "sales": "Sales",
    "purchases": "Purchases",
    "inventory": "Inventory",
    "reports": "Reports",
    "settings": "Settings",
    "operational": "Operational",
}

MODULE_META = {m.key: m for m in ALL_MODULES}


def humanize_field(key: str) -> str:
    if key in FIELD_LABELS:
        return FIELD_LABELS[key]
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", key)
    spaced = spaced.replace("_", " ").strip()
    return spaced[:1].upper() + spaced[1:] if spaced else key


def label_record(record: dict) -> dict:
    out: dict = {}
    for key, val in record.items():
        label = humanize_field(key)
        if isinstance(val, dict):
            out[label] = {humanize_field(k): v for k, v in val.items()}
        elif isinstance(val, list) and val and isinstance(val[0], dict):
            out[label] = [{humanize_field(k): v for k, v in row.items()} for row in val]
        else:
            out[label] = val
    return out


def build_labeled_export(source: Path, dest: Path) -> dict:
    data = json.loads(source.read_text(encoding="utf-8"))
    sections: list[dict] = []

    for module_key, mod in data.get("modules", {}).items():
        if module_key == "discovered_sidebar_links":
            continue
        meta = MODULE_META.get(module_key)
        records = mod.get("records") or []
        if not records:
            continue

        field_keys = sorted({k for r in records if isinstance(r, dict) for k in r})
        field_labels = {k: humanize_field(k) for k in field_keys}

        sections.append({
            "moduleKey": module_key,
            "moduleLabel": mod.get("label") or (meta.label if meta else module_key),
            "category": CATEGORY_LABELS.get(meta.category if meta else "operational", "Other"),
            "categoryKey": meta.category if meta else "operational",
            "sourceUrl": mod.get("sourceUrl", ""),
            "recordCount": len(records),
            "fieldLabels": field_labels,
            "records": [label_record(r) for r in records if isinstance(r, dict)],
        })

    sections.sort(key=lambda s: (s["categoryKey"], s["moduleLabel"]))

    total_records = sum(s["recordCount"] for s in sections)
    return {
        "exportedAt": datetime.now(timezone.utc).isoformat(),
        "sourceFile": source.name,
        "account": data.get("account", {}),
        "baseUrl": data.get("baseUrl", ""),
        "totalSections": len(sections),
        "totalRecords": total_records,
        "sections": sections,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Create labeled FastAccounts data export")
    parser.add_argument(
        "-i",
        "--input",
        default=str(OUTPUT_DIR / "fastaccounts_export_complete.json"),
        help="Source merged export JSON",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=str(OUTPUT_DIR / "fastaccounts_labeled_data.json"),
        help="Output labeled JSON path",
    )
    args = parser.parse_args()

    source = Path(args.input)
    dest = Path(args.output)
    if not source.exists():
        raise SystemExit(f"Source not found: {source}. Run export_fastaccounts_data.py first.")

    print(f"Reading {source.name} ({round(source.stat().st_size / 1024 / 1024, 1)} MB)...")
    labeled = build_labeled_export(source, dest)
    dest.write_text(json.dumps(labeled, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    size_mb = round(dest.stat().st_size / 1024 / 1024, 2)
    print(f"Wrote {dest.name} ({size_mb} MB)")
    print(f"Sections: {labeled['totalSections']}, Records: {labeled['totalRecords']}")
    for s in labeled["sections"]:
        print(f"  [{s['category']}] {s['moduleLabel']}: {s['recordCount']} records")


if __name__ == "__main__":
    main()
