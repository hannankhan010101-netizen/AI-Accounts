"""Email sales invoices to customers — P5."""

from __future__ import annotations

from decimal import Decimal

from app.repositories.company_repository import CompanyRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.sales_invoice_repository import SalesInvoiceRepository
from app.services.app_settings_service import AppSettingsService
from app.services.email_service import EmailService


class SalesInvoiceEmailService:
    def __init__(
        self,
        *,
        invoice_repo: SalesInvoiceRepository,
        customer_repo: CustomerRepository,
        company_repo: CompanyRepository,
        app_settings: AppSettingsService,
        email_service: EmailService,
    ) -> None:
        self._invoices = invoice_repo
        self._customers = customer_repo
        self._companies = company_repo
        self._settings = app_settings
        self._email = email_service

    async def send_invoice_email(
        self,
        *,
        company_id: str,
        invoice_id: str,
        to_email: str | None = None,
    ) -> dict[str, str | bool]:
        email_settings = await self._settings.get_email_settings(company_id=company_id)
        if not email_settings.get("sendInvoiceEmail"):
            raise ValueError(
                "Invoice email is disabled — enable it under Settings → Email settings"
            )

        invoice = await self._invoices.get_invoice(
            company_id=company_id, invoice_id=invoice_id
        )
        if invoice is None:
            raise ValueError("Invoice not found")
        if invoice.status not in {"posted", "draft"}:
            raise ValueError("Cannot email voided or reversed invoices")

        customer = await self._customers.get_customer(
            company_id=company_id, customer_id=invoice.customerId
        )
        if customer is None:
            raise ValueError("Customer not found")

        recipient = (to_email or customer.email or "").strip()
        if not recipient:
            raise ValueError("Customer has no email address — add one or pass to= in the request")

        company_name = await self._companies.get_company_name(company_id=company_id)
        subject = f"Invoice {invoice.invoiceNumber} — {company_name}"
        text, html = self._build_bodies(
            company_name=company_name,
            invoice_number=invoice.invoiceNumber,
            invoice_date=invoice.invoiceDate,
            customer_name=customer.name,
            total=str(invoice.totalAmount),
            lines=invoice.lines or [],
        )
        sent = await self._email.send_transactional_email(
            to=recipient, subject=subject, text=text, html=html
        )
        if sent:
            await self._settings.append_sent_email(
                company_id=company_id,
                entry={
                    "to": recipient,
                    "subject": subject,
                    "status": "sent",
                    "kind": "sales_invoice",
                    "documentId": invoice_id,
                },
            )
        return {"emailSent": sent, "to": recipient, "invoiceId": invoice_id}

    @staticmethod
    def _build_bodies(
        *,
        company_name: str,
        invoice_number: str,
        invoice_date,
        customer_name: str,
        total: str,
        lines,
    ) -> tuple[str, str]:
        date_str = invoice_date.strftime("%Y-%m-%d") if invoice_date else "—"
        line_rows: list[str] = []
        html_rows: list[str] = []
        for line in lines:
            code = getattr(line, "productCode", "") or "—"
            qty = getattr(line, "quantity", "")
            rate = getattr(line, "rate", "")
            amount = getattr(line, "lineTotal", "")
            line_rows.append(f"  {code}  qty={qty}  rate={rate}  amount={amount}")
            html_rows.append(
                "<tr>"
                f"<td>{code}</td><td>{qty}</td><td>{rate}</td><td>{amount}</td>"
                "</tr>"
            )
        try:
            total_fmt = Decimal(str(total)).quantize(Decimal("0.01"))
        except Exception:  # noqa: BLE001
            total_fmt = total

        text = (
            f"Dear {customer_name},\n\n"
            f"Please find invoice {invoice_number} dated {date_str} from {company_name}.\n\n"
            "Lines:\n"
            + ("\n".join(line_rows) if line_rows else "  (no lines)")
            + f"\n\nTotal: {total_fmt}\n\n"
            "Thank you for your business.\n"
        )
        html = (
            f"<p>Dear {customer_name},</p>"
            f"<p>Please find invoice <strong>{invoice_number}</strong> "
            f"dated {date_str} from {company_name}.</p>"
            "<table border='1' cellpadding='6' cellspacing='0'>"
            "<thead><tr><th>Product</th><th>Qty</th><th>Rate</th><th>Amount</th></tr></thead>"
            f"<tbody>{''.join(html_rows)}</tbody>"
            f"</table><p><strong>Total: {total_fmt}</strong></p>"
            "<p>Thank you for your business.</p>"
        )
        return text, html
