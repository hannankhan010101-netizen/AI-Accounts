"""Sign-up, email OTP, password reset, login, refresh, and company switching."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from jose import JWTError

from app.constants import auth_purposes as otp_purpose
from app.core.config import get_settings
from app.core.exceptions import ConflictError, ForbiddenError, UnauthorizedError, ValidationAppError
from app.core.otp import generate_six_digit_otp, hash_otp, otp_expiry, verify_otp
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.models.requests.auth_requests import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    ResendOtpRequest,
    ResetPasswordRequest,
    SignUpRequest,
    UpdateProfileRequest,
    VerifyEmailRequest,
)
from app.models.responses.auth_responses import AuthMessageResponse, SignUpPendingResponse, UserProfileResponse
from app.models.responses.common import AuthTokensResponse
from app.repositories.auth_otp_repository import AuthOtpRepository
from app.repositories.company_bootstrap_repository import CompanyBootstrapRepository
from app.repositories.company_repository import CompanyRepository
from app.repositories.user_repository import UserRepository
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)


class AuthService:
    """Registers tenants, verifies email, resets password, and issues JWTs."""

    def __init__(
        self,
        *,
        user_repository: UserRepository,
        company_repository: CompanyRepository,
        bootstrap_repository: CompanyBootstrapRepository,
        otp_repository: AuthOtpRepository,
        email_service: EmailService,
    ) -> None:
        self._users = user_repository
        self._companies = company_repository
        self._bootstrap = bootstrap_repository
        self._otp = otp_repository
        self._email = email_service

    async def sign_up(self, *, request: SignUpRequest) -> SignUpPendingResponse:
        """
        Create user, company, and defaults; email signup OTP when SMTP is configured.

        Does **not** return API tokens until ``verify_email`` succeeds.
        """

        existing = await self._users.find_by_email(email=request.email)
        if existing:
            raise ConflictError("Email already registered")
        password_hash = hash_password(request.password)
        user = await self._users.create(
            email=request.email,
            password_hash=password_hash,
            first_name=request.first_name,
            last_name=request.last_name,
            email_verified=False,
        )
        company = await self._companies.create_company(name=request.company_name)
        await self._companies.add_membership(
            company_id=company.id,
            user_id=user.id,
            is_default=True,
            role_id=None,
        )
        await self._bootstrap.create_phase1_defaults(company_id=company.id)
        await self._bootstrap.assign_admin_role(company_id=company.id, user_id=user.id)
        expires_at, plain = await self._store_otp(
            user_id=user.id,
            email=request.email,
            purpose=otp_purpose.SIGNUP,
        )
        email_sent = await self._email.send_otp_email(
            to=request.email,
            code=plain,
            purpose=otp_purpose.SIGNUP,
        )
        logger.info(
            "Registered user %s company %s pending email verify (otp_email_sent=%s)",
            user.id,
            company.id,
            email_sent,
        )
        return self._pending_response(
            email=request.email,
            expires_at=expires_at,
            plain_otp=plain,
            email_sent=email_sent,
        )

    async def verify_email(self, *, request: VerifyEmailRequest) -> AuthTokensResponse:
        """Validate signup OTP and activate the account."""

        user = await self._users.find_by_email(email=request.email)
        if user is None:
            raise UnauthorizedError("Invalid email or code")
        if user.emailVerified:
            raise ValidationAppError("Email is already verified")
        await self._assert_valid_otp(
            user_id=user.id,
            email=request.email,
            purpose=otp_purpose.SIGNUP,
            code=request.otp_code,
        )
        await self._otp.delete_for_user_purpose(user_id=user.id, purpose=otp_purpose.SIGNUP)
        await self._users.update_email_verified(user_id=user.id, verified=True)
        company_id = await self._companies.get_default_company_id_for_user(user_id=user.id)
        if company_id is None:
            raise UnauthorizedError("User has no company membership")
        await self._ensure_founding_role(company_id=company_id, user_id=user.id)
        return self._issue_tokens(user_id=user.id, company_id=company_id)

    async def resend_otp(self, *, request: ResendOtpRequest) -> SignUpPendingResponse | AuthMessageResponse:
        """Issue a new OTP for signup (unverified) or password reset (verified)."""

        user = await self._users.find_by_email(email=request.email)
        if user is None:
            return AuthMessageResponse(message="If the account exists, a code has been sent.")
        if request.purpose == otp_purpose.SIGNUP:
            if user.emailVerified:
                return AuthMessageResponse(message="If the account exists, a code has been sent.")
            expires_at, plain = await self._store_otp(
                user_id=user.id,
                email=request.email,
                purpose=otp_purpose.SIGNUP,
            )
            email_sent = await self._email.send_otp_email(
                to=request.email,
                code=plain,
                purpose=otp_purpose.SIGNUP,
            )
            return self._pending_response(
                email=request.email,
                expires_at=expires_at,
                plain_otp=plain,
                email_sent=email_sent,
            )
        if request.purpose == otp_purpose.PASSWORD_RESET:
            if not user.emailVerified:
                return AuthMessageResponse(message="If the account exists, a code has been sent.")
            expires_at, plain = await self._store_otp(
                user_id=user.id,
                email=request.email,
                purpose=otp_purpose.PASSWORD_RESET,
            )
            email_sent = await self._email.send_otp_email(
                to=request.email,
                code=plain,
                purpose=otp_purpose.PASSWORD_RESET,
            )
            return self._pending_response(
                email=request.email,
                expires_at=expires_at,
                plain_otp=plain,
                email_sent=email_sent,
            )
        raise ValidationAppError("Unsupported purpose")

    async def forgot_password(
        self, *, request: ForgotPasswordRequest
    ) -> SignUpPendingResponse | AuthMessageResponse:
        """Issue password-reset OTP for verified accounts; signup OTP if still unverified."""

        user = await self._users.find_by_email(email=request.email)
        if user is None:
            return AuthMessageResponse(message="If the account exists, a code has been sent.")
        if not user.emailVerified:
            expires_at, plain = await self._store_otp(
                user_id=user.id,
                email=request.email,
                purpose=otp_purpose.SIGNUP,
            )
            email_sent = await self._email.send_otp_email(
                to=request.email,
                code=plain,
                purpose=otp_purpose.SIGNUP,
            )
            return self._pending_response(
                email=request.email,
                expires_at=expires_at,
                plain_otp=plain,
                email_sent=email_sent,
            )
        expires_at, plain = await self._store_otp(
            user_id=user.id,
            email=request.email,
            purpose=otp_purpose.PASSWORD_RESET,
        )
        email_sent = await self._email.send_otp_email(
            to=request.email,
            code=plain,
            purpose=otp_purpose.PASSWORD_RESET,
        )
        return self._pending_response(
            email=request.email,
            expires_at=expires_at,
            plain_otp=plain,
            email_sent=email_sent,
            flow="password_reset",
        )

    async def reset_password(self, *, request: ResetPasswordRequest) -> AuthMessageResponse:
        """Apply a new password after OTP validation."""

        user = await self._users.find_by_email(email=request.email)
        if user is None:
            raise UnauthorizedError("Invalid email or code")
        if request.purpose == otp_purpose.PASSWORD_RESET and not user.emailVerified:
            raise UnauthorizedError("Invalid email or code")
        await self._assert_valid_otp(
            user_id=user.id,
            email=request.email,
            purpose=request.purpose,
            code=request.otp_code,
        )
        await self._otp.delete_for_user_purpose(user_id=user.id, purpose=request.purpose)
        await self._users.update_password_hash(
            user_id=user.id,
            password_hash=hash_password(request.new_password),
        )
        if request.purpose == otp_purpose.USER_INVITE and not user.emailVerified:
            await self._users.update_email_verified(user_id=user.id, verified=True)
        if request.purpose == otp_purpose.USER_INVITE:
            return AuthMessageResponse(
                message="Password set. You can sign in now.",
            )
        return AuthMessageResponse(message="Password has been reset. You can sign in now.")

    async def send_invite_setup_email(
        self,
        *,
        user_id: str,
        email: str,
        company_name: str,
        invite_template: dict[str, str],
    ) -> bool:
        """Issue USER_INVITE OTP and email a set-password link — P28/P30."""

        from urllib.parse import quote

        from app.services.invite_email_template_service import apply_placeholders

        settings = get_settings()
        _expires_at, plain = await self._store_otp(
            user_id=user_id,
            email=email,
            purpose=otp_purpose.USER_INVITE,
        )
        link = (
            f"{settings.app_public_url.rstrip('/')}/reset-password"
            f"?email={quote(email)}&invite=1"
        )
        rendered = apply_placeholders(
            invite_template,
            companyName=company_name,
            resetLink=link,
            code=plain,
            ttlMinutes=str(settings.otp_ttl_minutes),
        )
        return await self._email.send_invite_email(
            to=email,
            subject=rendered["subject"],
            text=rendered["introText"],
            html=rendered["introHtml"],
        )

    async def refresh_tokens(self, *, request: RefreshRequest) -> AuthTokensResponse:
        """Issue a new access token (and rotated refresh) from a valid refresh JWT."""

        try:
            payload = decode_refresh_token(request.refresh_token)
        except JWTError as exc:
            raise UnauthorizedError("Invalid refresh token") from exc
        user_id = payload.get("sub")
        if not isinstance(user_id, str):
            raise UnauthorizedError("Invalid refresh token")
        user = await self._users.find_by_id(user_id=user_id)
        if user is None or not user.isActive:
            raise UnauthorizedError("Invalid refresh token")
        if not user.emailVerified:
            raise ForbiddenError("Email address is not verified")
        company_id: str | None = request.company_id
        if company_id is not None:
            allowed = await self._companies.user_belongs_to_company(
                user_id=user.id, company_id=company_id
            )
            if not allowed:
                company_id = None
        if company_id is None:
            company_id = await self._companies.get_default_company_id_for_user(user_id=user.id)
        if company_id is None:
            raise UnauthorizedError("User has no company membership")
        return self._issue_tokens(user_id=user.id, company_id=company_id)

    async def create_company_for_user(
        self,
        *,
        user_id: str,
        request: CreateCompanyRequest,
    ) -> dict:
        """Create another company and link the current user (non-default membership)."""

        company = await self._companies.create_company(name=request.name)
        await self._companies.add_membership(
            company_id=company.id,
            user_id=user_id,
            is_default=False,
            role_id=None,
        )
        await self._bootstrap.create_phase1_defaults(company_id=company.id)
        await self._bootstrap.assign_admin_role(company_id=company.id, user_id=user_id)
        return {
            "id": company.id,
            "companyId": company.id,
            "name": company.name,
        }

    async def switch_company(self, *, user_id: str, company_id: str) -> AuthTokensResponse:
        """Re-issue tokens after validating membership."""

        allowed = await self._companies.user_belongs_to_company(user_id=user_id, company_id=company_id)
        if not allowed:
            raise ForbiddenError("User is not a member of this company")
        return self._issue_tokens(user_id=user_id, company_id=company_id)

    async def login(self, *, request: LoginRequest) -> AuthTokensResponse:
        """Validate password and mint tokens for default company."""

        user = await self._users.find_by_email(email=request.email)
        if user is None or not verify_password(request.password, user.passwordHash):
            raise UnauthorizedError("Invalid email or password")
        if not user.emailVerified:
            raise ForbiddenError("Email address is not verified. Complete OTP verification first.")
        company_id = await self._companies.get_default_company_id_for_user(user_id=user.id)
        if company_id is None:
            raise UnauthorizedError("User has no company membership")
        await self._ensure_founding_role(company_id=company_id, user_id=user.id)
        return self._issue_tokens(user_id=user.id, company_id=company_id)

    async def _ensure_founding_role(self, *, company_id: str, user_id: str) -> None:
        """Backfill Super Admin when company bootstrap did not attach a membership role."""

        await self._bootstrap.seed_missing_template_roles(company_id=company_id)
        await self._bootstrap.assign_admin_role(company_id=company_id, user_id=user_id)

    def _issue_tokens(self, *, user_id: str, company_id: str) -> AuthTokensResponse:
        """Build access and refresh JWTs embedding active company."""

        access = create_access_token(
            subject=user_id,
            extra_claims={"companyId": company_id},
        )
        refresh = create_refresh_token(subject=user_id)
        return AuthTokensResponse(access_token=access, refresh_token=refresh)

    def _pending_response(
        self,
        *,
        email: str,
        expires_at: datetime,
        plain_otp: str,
        email_sent: bool = True,
        flow: str = "signup",
    ) -> SignUpPendingResponse:
        """Build pending response; include code in API when email could not be delivered."""

        settings = get_settings()
        expose = (
            settings.auth_expose_otp_in_response
            or not self._email.is_configured()
            or not email_sent
        )
        dev = plain_otp if expose else None
        if email_sent:
            message = (
                "Password reset code sent to your email."
                if flow == "password_reset"
                else "Verification code sent to your email. Complete verification to sign in."
            )
        else:
            message = (
                "We could not deliver the email (invalid or blocked address). "
                "Use the verification code shown below, or sign up with a real inbox "
                "(e.g. Gmail) and check spam."
            )
            logger.warning("OTP not delivered to %s — returning code in API response", email)
        return SignUpPendingResponse(
            message=message,
            email=email,
            expires_at=expires_at,
            dev_otp=dev,
        )

    async def _store_otp(self, *, user_id: str, email: str, purpose: str) -> tuple[datetime, str]:
        """Persist a new OTP digest and return expiry plus plaintext for dev echo."""

        settings = get_settings()
        await self._otp.delete_for_user_purpose(user_id=user_id, purpose=purpose)
        plain = generate_six_digit_otp()
        digest = hash_otp(email=email, purpose=purpose, code=plain)
        expires_at = otp_expiry(ttl_minutes=settings.otp_ttl_minutes)
        await self._otp.create(user_id=user_id, purpose=purpose, code_hash=digest, expires_at=expires_at)
        return expires_at, plain

    async def _assert_valid_otp(self, *, user_id: str, email: str, purpose: str, code: str) -> None:
        """Raise when no valid challenge matches the submitted code."""

        challenge = await self._otp.find_latest_for_user_purpose(user_id=user_id, purpose=purpose)
        if challenge is None:
            raise UnauthorizedError("Invalid email or code")
        now = datetime.now(tz=UTC)
        exp = challenge.expiresAt
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=UTC)
        if now > exp:
            raise UnauthorizedError("Code has expired")
        if not verify_otp(email=email, purpose=purpose, code=code, code_hash=challenge.codeHash):
            raise UnauthorizedError("Invalid email or code")

    async def get_profile(self, *, user_id: str) -> UserProfileResponse:
        """Return profile for the signed-in user."""

        user = await self._users.find_by_id(user_id=user_id)
        if user is None:
            raise UnauthorizedError("User not found")
        return UserProfileResponse(
            id=user.id,
            email=user.email,
            first_name=user.firstName,
            last_name=user.lastName,
            phone=user.phone,
            email_verified=user.emailVerified,
        )

    async def update_profile(
        self, *, user_id: str, request: UpdateProfileRequest
    ) -> UserProfileResponse:
        """Patch profile fields."""

        if request.first_name is None and request.last_name is None and request.phone is None:
            raise ValidationAppError("No profile fields to update")
        user = await self._users.update_profile(
            user_id=user_id,
            first_name=request.first_name,
            last_name=request.last_name,
            phone=request.phone,
        )
        return UserProfileResponse(
            id=user.id,
            email=user.email,
            first_name=user.firstName,
            last_name=user.lastName,
            phone=user.phone,
            email_verified=user.emailVerified,
        )

    async def change_password(
        self, *, user_id: str, request: ChangePasswordRequest
    ) -> AuthMessageResponse:
        """Change password when the current password is known."""

        user = await self._users.find_by_id(user_id=user_id)
        if user is None:
            raise UnauthorizedError("User not found")
        if not verify_password(request.current_password, user.passwordHash):
            raise UnauthorizedError("Current password is incorrect")
        if request.current_password == request.new_password:
            raise ValidationAppError("New password must differ from the current password")
        await self._users.update_password_hash(
            user_id=user_id,
            password_hash=hash_password(request.new_password),
        )
        return AuthMessageResponse(message="Password updated successfully.")
