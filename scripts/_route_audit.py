#!/usr/bin/env python3
"""Audit nav/settings/reports hrefs vs Frontend pages."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
pages = {
    str(p.relative_to(ROOT)).replace("\\", "/")
    for p in (ROOT / "Frontend/src/app/(app)").rglob("page.tsx")
}


def extract_hrefs(text: str) -> set[str]:
    return set(re.findall(r'href:\s*"([^"]+)"', text))


def has_page(href: str) -> bool:
    if href.startswith("/reports/extended/"):
        return "Frontend/src/app/(app)/reports/extended/[slug]/page.tsx" in pages
    if href.startswith("/settings/printing/"):
        return "Frontend/src/app/(app)/settings/printing/[code]/page.tsx" in pages
    path = href.strip("/")
    if not path:
        return False
    return f"Frontend/src/app/(app)/{path}/page.tsx" in pages


for name in ("navigation.ts", "settings-menu.ts", "reports-catalog.ts"):
    text = (ROOT / "Frontend/src/config" / name).read_text(encoding="utf-8")
    hrefs = extract_hrefs(text)
    stub = sorted(h for h in hrefs if not has_page(h))
    real = sorted(h for h in hrefs if has_page(h))
    print(f"\n=== {name} ===")
    print(f"  with page: {len(real)}, stub: {len(stub)}")
    for h in stub:
        print(f"    STUB {h}")
