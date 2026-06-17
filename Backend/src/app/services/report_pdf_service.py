"""Simple PDF export for completed report runs — P4."""

from __future__ import annotations

import io
from typing import Any


def rows_to_pdf(*, title: str, rows: list[dict[str, Any]]) -> bytes:
    try:
        from fpdf import FPDF
    except ImportError as exc:
        raise RuntimeError(
            "PDF export requires fpdf2. Install with: pip install fpdf2"
        ) from exc

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=9)

    if not rows:
        pdf.cell(0, 8, "No rows.", new_x="LMARGIN", new_y="NEXT")
    else:
        headers = list(rows[0].keys())
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(0, 6, " | ".join(str(h) for h in headers), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=8)
        for row in rows[:500]:
            line = " | ".join(str(row.get(h, ""))[:40] for h in headers)
            pdf.cell(0, 5, line, new_x="LMARGIN", new_y="NEXT")

    out = io.BytesIO()
    pdf.output(out)
    return out.getvalue()
