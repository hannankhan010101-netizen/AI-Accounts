"""Sales invoice email body builder."""

from datetime import datetime, timezone
from types import SimpleNamespace

from app.services.sales_invoice_email_service import SalesInvoiceEmailService


def test_build_bodies_includes_lines_and_total() -> None:
    lines = [
        SimpleNamespace(productCode="P001", quantity="2", rate="100", lineTotal="200"),
    ]
    text, html = SalesInvoiceEmailService._build_bodies(
        company_name="Nafy Pharma",
        invoice_number="SI-100",
        invoice_date=datetime(2026, 5, 29, tzinfo=timezone.utc),
        customer_name="Acme",
        total="200",
        lines=lines,
    )
    assert "SI-100" in text
    assert "P001" in text
    assert "200.00" in text
    assert "SI-100" in html
    assert "P001" in html
