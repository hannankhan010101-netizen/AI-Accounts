"""Report pivot helpers — P16."""

from __future__ import annotations

import csv
import io
from typing import Any


def build_pnl_category_pivot(flat_rows: list[dict[str, Any]]) -> dict[str, Any]:
    periods = sorted({str(r.get("period") or "") for r in flat_rows if r.get("period")})
    keyed: dict[tuple[str, str], dict[str, Any]] = {}
    for row in flat_rows:
        ctype = str(row.get("categoryType") or "")
        cname = str(row.get("categoryName") or "")
        key = (ctype, cname)
        if key not in keyed:
            keyed[key] = {
                "categoryType": ctype,
                "categoryName": cname,
                "amounts": {},
            }
        keyed[key]["amounts"][str(row.get("period") or "")] = row.get("amount")
    pivot_rows = sorted(
        keyed.values(),
        key=lambda r: (r["categoryType"], r["categoryName"]),
    )
    return {"periods": periods, "rows": pivot_rows}


def pivot_pnl_category_to_csv(pivot: dict[str, Any]) -> str:
    periods: list[str] = list(pivot.get("periods") or [])
    rows: list[dict[str, Any]] = list(pivot.get("rows") or [])
    buf = io.StringIO()
    fieldnames = ["categoryType", "categoryName", *periods]
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        amounts = row.get("amounts") if isinstance(row.get("amounts"), dict) else {}
        out: dict[str, str] = {
            "categoryType": str(row.get("categoryType") or ""),
            "categoryName": str(row.get("categoryName") or ""),
        }
        for period in periods:
            out[period] = str(amounts.get(period) or "")
        writer.writerow(out)
    return buf.getvalue()
