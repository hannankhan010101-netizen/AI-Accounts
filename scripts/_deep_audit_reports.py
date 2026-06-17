#!/usr/bin/env python3
"""Report handler gap analysis."""
from __future__ import annotations

import inspect
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Backend" / "src"))

from app.constants.report_aliases import resolve_report_handler_id
from app.constants.report_catalog_registry import CATALOG_REPORT_IDS
from app.constants.report_definitions import all_report_definitions
from app.services.report_query_service import ReportQueryService

src = inspect.getsource(ReportQueryService.execute)
handlers: set[str] = set()
for m in re.finditer(r'"([A-Z0-9_]+)":', src):
    handlers.add(m.group(1))
for m in re.finditer(r'"(\d+)":', src):
    handlers.add(m.group(1))

unmapped = []
for rid in sorted(CATALOG_REPORT_IDS, key=lambda x: (not str(x).isdigit(), str(x))):
    hk = resolve_report_handler_id(rid)
    if hk not in handlers:
        unmapped.append((rid, hk))

print(f"SQL handlers in ReportQueryService: {len(handlers)}")
print(f"CATALOG_REPORT_IDS unmapped: {len(unmapped)}")
for rid, hk in unmapped:
    print(f"  {rid} -> {hk}")

no_handler = []
for r in all_report_definitions():
    hk = resolve_report_handler_id(r.report_id)
    if hk not in handlers:
        no_handler.append((r.hub, r.report_id, r.name, hk))

print(f"\nDefinition rows ({len(all_report_definitions())}) without handler: {len(no_handler)}")
hubs: dict[str, int] = {}
for h, *_ in no_handler:
    hubs[h] = hubs.get(h, 0) + 1
for h, n in sorted(hubs.items(), key=lambda x: -x[1]):
    print(f"  {h}: {n}")
if no_handler:
    print("\nMissing handler details:")
    for h, rid, name, hk in no_handler:
        print(f"  hub={h} id={rid} name={name!r} resolved={hk}")
