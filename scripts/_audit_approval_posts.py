#!/usr/bin/env python3
"""List tenant POST routes that post GL amounts but lack assert_can_post / guard_document_post."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TENANT = ROOT / "Backend/src/app/api/routes/tenant.py"

POST_ROUTE = re.compile(r'@router\.post\("([^"]+)"')
HAS_GUARD = re.compile(r"guard_document_post|assert_can_post")
HAS_POSTING = re.compile(
    r"posting_service\.post_|posting_engine\.approve_|\.post_draft\("
)

GUARDED_PREFIXES = (
    "/sales-invoices/{invoice_id}/approve",
    "/supplier-bills/{bill_id}/approve",
    "/journals/{journal_id}/post",
    "/sales-credits",
    "/supplier-credits",
    "/sales-receipts",
    "/supplier-payments",
    "/bank-payments",
    "/bank-receipts",
    "/bank-transfers",
)


def main() -> None:
    text = TENANT.read_text(encoding="utf-8")
    blocks = text.split("@router.post")
    missing: list[str] = []
    for block in blocks[1:]:
        m = re.match(r'\("([^"]+)"', block)
        if not m:
            continue
        route = m.group(1)
        if not HAS_POSTING.search(block):
            continue
        if HAS_GUARD.search(block):
            continue
        if any(route.startswith(p.split("{")[0]) for p in GUARDED_PREFIXES if "{" not in p):
            if route in (p.replace("{invoice_id}", "").replace("{bill_id}", "") for p in GUARDED_PREFIXES):
                continue
        missing.append(route)

    print("POST routes with GL posting but no approval guard in block:")
    for r in sorted(set(missing)):
        print(f"  {r}")
    print(f"\nTotal: {len(set(missing))}")


if __name__ == "__main__":
    main()
