#!/usr/bin/env python3
"""Add print template wiring to voucher print pages."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "Frontend/src/app/print"
CODES = {
    "bank-payment": "bank",
    "bank-receipt": "bank",
    "bank-transfer": "bank",
    "journal": "journal",
    "pdc-received": "pdcr",
    "pdc-issued": "pdci",
    "stock-adjustment": "stock-adjustment",
    "stock-transfer": "stock-transfer",
    "grn": "grnpo",
    "delivery-notes": "gdnsi",
}

for folder, code in CODES.items():
    for path in ROOT.glob(f"{folder}/**/page.tsx"):
        text = path.read_text(encoding="utf-8")
        if "template={template}" in text:
            continue
        text = text.replace(
            "businessAddress, isLoading, error } = useVoucherPrintPage(",
            "businessAddress, template, isLoading, error } = useVoucherPrintPage(",
        )
        text = re.sub(
            r"(useVoucherPrintPage\(\s*\[[^\]]+\],\s*\(\) => [^,]+,\s*!!params\.id,\s*)\)",
            rf'\1\n    "{code}",\n  )',
            text,
            count=1,
        )
        if "<VoucherPrint" in text:
            text = text.replace(
                "businessAddress={businessAddress}",
                "businessAddress={businessAddress}\n          template={template}",
                1,
            )
        path.write_text(text, encoding="utf-8")
        print("updated", path.relative_to(ROOT.parent.parent))
