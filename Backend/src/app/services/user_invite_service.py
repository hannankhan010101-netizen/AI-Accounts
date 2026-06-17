"""Post-invite email and setup orchestration — P28/P29/P30."""

from __future__ import annotations

from app.core.config import get_settings
from app.repositories.company_repository import CompanyRepository
from app.repositories.membership_repository import MembershipRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.services.invite_email_template_service import (
    InviteEmailTemplateService,
    apply_placeholders,
)


class UserInviteService:
    """Send set-password or welcome mail for company members."""

    def __init__(
        self,
        *,
        auth_service: AuthService,
        company_repository: CompanyRepository,
        user_repository: UserRepository,
        membership_repository: MembershipRepository,
        email_service: EmailService,
        template_service: InviteEmailTemplateService,
    ) -> None:
        self._auth = auth_service
        self._companies = company_repository
        self._users = user_repository
        self._memberships = membership_repository
        self._email = email_service
        self._templates = template_service

    async def send_setup_email_if_needed(
        self,
        *,
        company_id: str,
        user_id: str,
        email: str,
        user_created: bool,
    ) -> bool:
        """Return True when invite or welcome email was sent."""

        user = await self._users.find_by_id(user_id=user_id)
        if user is None:
            return False
        company_name = await self._companies.get_company_name(company_id=company_id)
        if not user_created and user.emailVerified:
            return await self._send_welcome(
                company_id=company_id,
                email=email,
                company_name=company_name,
            )
        return await self._send_setup(
            company_id=company_id,
            user_id=user_id,
            email=email,
            company_name=company_name,
        )

    async def resend_invite_email(
        self,
        *,
        company_id: str,
        user_id: str,
    ) -> dict[str, str | bool]:
        """Resend setup OTP email or welcome mail for a company member."""

        membership = await self._memberships.get_membership(
            company_id=company_id,
            user_id=user_id,
        )
        if membership is None:
            raise ValueError("User is not a member of this company")
        email = str(membership["user"]["email"])
        user = await self._users.find_by_id(user_id=user_id)
        if user is None:
            raise ValueError("User not found")
        company_name = await self._companies.get_company_name(company_id=company_id)
        if user.emailVerified:
            sent = await self._send_welcome(
                company_id=company_id,
                email=email,
                company_name=company_name,
            )
            return {"emailType": "welcome", "emailSent": sent, "email": email}
        sent = await self._send_setup(
            company_id=company_id,
            user_id=user_id,
            email=email,
            company_name=company_name,
        )
        return {"emailType": "setup", "emailSent": sent, "email": email}

    async def _send_setup(
        self,
        *,
        company_id: str,
        user_id: str,
        email: str,
        company_name: str,
    ) -> bool:
        tpl = await self._templates.get_invite_template(company_id=company_id)
        return await self._auth.send_invite_setup_email(
            user_id=user_id,
            email=email,
            company_name=company_name,
            invite_template=tpl,
        )

    async def _send_welcome(
        self,
        *,
        company_id: str,
        email: str,
        company_name: str,
    ) -> bool:
        settings = get_settings()
        login_url = settings.app_public_url.rstrip("/") + "/login"
        tpl = await self._templates.get_welcome_template(company_id=company_id)
        rendered = apply_placeholders(
            tpl,
            companyName=company_name,
            loginUrl=login_url,
        )
        return await self._email.send_welcome_email(
            to=email,
            subject=rendered["subject"],
            text=rendered["introText"],
            html=rendered["introHtml"],
        )
