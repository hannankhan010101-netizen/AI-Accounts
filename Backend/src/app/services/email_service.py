"""Send OTP and transactional mail via Brevo API or SMTP fallback."""

from __future__ import annotations

import asyncio
import logging
import smtplib
from email.message import EmailMessage

import httpx

from app.constants import auth_purposes as otp_purpose
from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"

_PURPOSE_COPY: dict[str, tuple[str, str]] = {
    otp_purpose.SIGNUP: (
        "Verify your Fast Accounts email",
        "Use this code to complete sign-up:",
    ),
    otp_purpose.PASSWORD_RESET: (
        "Reset your Fast Accounts password",
        "Use this code to reset your password:",
    ),
    otp_purpose.USER_INVITE: (
        "Set your Fast Accounts password",
        "You were invited to join a company. Use this code to set your password:",
    ),
}


class EmailService:
    """Brevo (preferred) or generic SMTP mailer."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def _sender_email(self) -> str:
        """From address for outbound mail."""

        return self._settings.brevo_sender_email or self._settings.smtp_from_email

    def is_configured(self) -> bool:
        """True when Brevo API or SMTP relay can send mail."""

        s = self._settings
        if s.brevo_api_key and self._sender_email():
            return True
        return bool(s.smtp_host and self._sender_email() and s.smtp_user and s.smtp_password)

    def _build_content(self, *, code: str, purpose: str) -> tuple[str, str, str]:
        subject, intro = _PURPOSE_COPY.get(
            purpose,
            ("Your Fast Accounts verification code", "Your verification code is:"),
        )
        ttl = self._settings.otp_ttl_minutes
        text = (
            f"{intro}\n\n"
            f"  {code}\n\n"
            f"This code expires in {ttl} minutes.\n"
            "If you did not request this, you can ignore this email.\n"
        )
        html = (
            f"<p>{intro}</p>"
            f'<p style="font-size:24px;font-weight:bold;letter-spacing:4px">{code}</p>'
            f"<p>This code expires in {ttl} minutes.</p>"
            f"<p>If you did not request this, you can ignore this email.</p>"
        )
        return subject, text, html

    async def send_otp_email(self, *, to: str, code: str, purpose: str) -> bool:
        """
        Deliver a 6-digit OTP email via Brevo or SMTP.

        Returns True when send succeeded, False when skipped or failed.
        """

        if not self.is_configured():
            logger.warning(
                "Email not configured — OTP for %s (%s) was not sent. "
                "Set BREVO_API_KEY + BREVO_SENDER_EMAIL in .env "
                "(https://app.brevo.com) or enable AUTH_EXPOSE_OTP_IN_RESPONSE for local dev.",
                to,
                purpose,
            )
            return False

        subject, text, html = self._build_content(code=code, purpose=purpose)
        try:
            if self._settings.brevo_api_key:
                await self._send_brevo_api(to=to, subject=subject, text=text, html=html)
            else:
                await asyncio.to_thread(
                    self._send_smtp,
                    to=to,
                    subject=subject,
                    text=text,
                    html=html,
                )
            logger.info("OTP email sent to %s (%s)", to, purpose)
            return True
        except Exception:
            logger.exception("Failed to send OTP email to %s", to)
            return False

    async def send_invite_email(
        self,
        *,
        to: str,
        subject: str,
        text: str,
        html: str,
    ) -> bool:
        """Invite email with set-password link and OTP — P28/P30."""

        if not self.is_configured():
            logger.warning(
                "Email not configured — invite for %s was not sent. "
                "Set BREVO_API_KEY + BREVO_SENDER_EMAIL or SMTP in .env.",
                to,
            )
            return False
        try:
            if self._settings.brevo_api_key:
                await self._send_brevo_api(to=to, subject=subject, text=text, html=html)
            else:
                await asyncio.to_thread(
                    self._send_smtp,
                    to=to,
                    subject=subject,
                    text=text,
                    html=html,
                )
            logger.info("Invite email sent to %s", to)
            return True
        except Exception:
            logger.exception("Failed to send invite email to %s", to)
            return False

    async def send_welcome_email(
        self,
        *,
        to: str,
        subject: str,
        text: str,
        html: str,
    ) -> bool:
        """Notify an existing user they were added to a company — P29/P30."""

        if not self.is_configured():
            logger.warning("Email not configured — welcome for %s was not sent.", to)
            return False
        try:
            if self._settings.brevo_api_key:
                await self._send_brevo_api(to=to, subject=subject, text=text, html=html)
            else:
                await asyncio.to_thread(
                    self._send_smtp,
                    to=to,
                    subject=subject,
                    text=text,
                    html=html,
                )
            logger.info("Welcome email sent to %s", to)
            return True
        except Exception:
            logger.exception("Failed to send welcome email to %s", to)
            return False

    async def send_digest_email(
        self,
        *,
        to: str,
        subject: str,
        text: str,
        html: str,
    ) -> bool:
        """What's New product digest — P55."""

        if not self.is_configured():
            logger.warning("Email not configured — digest for %s was not sent.", to)
            return False
        try:
            if self._settings.brevo_api_key:
                await self._send_brevo_api(to=to, subject=subject, text=text, html=html)
            else:
                await asyncio.to_thread(
                    self._send_smtp,
                    to=to,
                    subject=subject,
                    text=text,
                    html=html,
                )
            logger.info("Onboarding digest sent to %s", to)
            return True
        except Exception:
            logger.exception("Failed to send digest to %s", to)
            return False

    async def send_transactional_email(
        self,
        *,
        to: str,
        subject: str,
        text: str,
        html: str,
    ) -> bool:
        """Generic transactional email (invoices, reminders, etc.)."""

        if not self.is_configured():
            logger.warning("Email not configured — message to %s was not sent.", to)
            return False
        try:
            if self._settings.brevo_api_key:
                await self._send_brevo_api(to=to, subject=subject, text=text, html=html)
            else:
                await asyncio.to_thread(
                    self._send_smtp,
                    to=to,
                    subject=subject,
                    text=text,
                    html=html,
                )
            logger.info("Transactional email sent to %s", to)
            return True
        except Exception:
            logger.exception("Failed to send transactional email to %s", to)
            return False

    async def _send_brevo_api(self, *, to: str, subject: str, text: str, html: str) -> None:
        """POST to Brevo transactional email API."""

        s = self._settings
        payload = {
            "sender": {
                "email": s.brevo_sender_email,
                "name": s.brevo_sender_name,
            },
            "to": [{"email": to}],
            "subject": subject,
            "htmlContent": html,
            "textContent": text,
            "tags": ["otp", "fast-accounts"],
        }
        headers = {
            "api-key": s.brevo_api_key,
            "accept": "application/json",
            "content-type": "application/json",
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(BREVO_API_URL, json=payload, headers=headers)
            response.raise_for_status()

    def _send_smtp(self, *, to: str, subject: str, text: str, html: str) -> None:
        """Blocking SMTP send (Brevo relay or other provider)."""

        s = self._settings
        from_email = self._sender_email()
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to
        msg.set_content(text)
        msg.add_alternative(html, subtype="html")

        with smtplib.SMTP(s.smtp_host, s.smtp_port, timeout=30) as client:
            if s.smtp_use_tls:
                client.starttls()
            if s.smtp_user and s.smtp_password:
                client.login(s.smtp_user, s.smtp_password)
            client.send_message(msg)
