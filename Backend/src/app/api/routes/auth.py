"""Authentication endpoints (no tenant guard)."""

from __future__ import annotations

from typing import Annotated, Union

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.dependencies.deps import get_auth_service, get_jwt_claims, JwtClaims
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
from app.models.responses.auth_responses import AuthMessageResponse, LogoutResponse, SignUpPendingResponse, UserProfileResponse
from app.models.responses.common import AuthTokensResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/sign-up", response_model=Union[SignUpPendingResponse, AuthTokensResponse], status_code=201)
async def sign_up(
    body: SignUpRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SignUpPendingResponse | AuthTokensResponse:
    """Register user and first company.

    Returns a pending response (verify email with OTP before login) unless
    ``AUTH_SKIP_EMAIL_VERIFICATION`` is enabled, in which case tokens are
    returned immediately.
    """

    return await auth_service.sign_up(request=body)


@router.post("/verify-email", response_model=AuthTokensResponse)
async def verify_email(
    body: VerifyEmailRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> AuthTokensResponse:
    """Submit signup email OTP to activate the account and receive tokens."""

    return await auth_service.verify_email(request=body)


@router.post("/resend-otp", response_model=Union[SignUpPendingResponse, AuthMessageResponse])
async def resend_otp(
    body: ResendOtpRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SignUpPendingResponse | AuthMessageResponse:
    """Resend signup or password-reset OTP (same response shape as sign-up when a code is issued)."""

    return await auth_service.resend_otp(request=body)


@router.post("/forgot-password", response_model=None)
async def forgot_password(
    body: ForgotPasswordRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SignUpPendingResponse | AuthMessageResponse:
    """Request password-reset OTP, or signup verification OTP when email is not verified yet."""

    return await auth_service.forgot_password(request=body)


@router.post("/reset-password", response_model=AuthMessageResponse)
async def reset_password(
    body: ResetPasswordRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> AuthMessageResponse:
    """Complete password reset with email OTP."""

    return await auth_service.reset_password(request=body)


@router.post("/accept-invite", response_model=AuthMessageResponse)
async def accept_invite(
    body: ResetPasswordRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> AuthMessageResponse:
    """Set password for an invited user (``purpose=user_invite``)."""

    from app.constants import auth_purposes as otp_purpose

    return await auth_service.reset_password(
        request=body.model_copy(update={"purpose": otp_purpose.USER_INVITE}),
    )


@router.post("/login", response_model=AuthTokensResponse)
async def login(
    request: Request,
    body: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> AuthTokensResponse:
    """Password login (requires verified email)."""

    from app.core.rate_limit import check_rate_limit

    try:
        check_rate_limit(request, group="auth")
    except PermissionError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc

    return await auth_service.login(request=body)


@router.post("/refresh", response_model=AuthTokensResponse)
async def refresh(
    body: RefreshRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> AuthTokensResponse:
    """Exchange refresh token for a new access token (and rotated refresh)."""

    return await auth_service.refresh_tokens(request=body)


@router.post("/logout", response_model=LogoutResponse)
async def logout() -> LogoutResponse:
    """
    Client-side logout hint.

    JWTs remain stateless until a blocklist or session store is added.
    """

    return LogoutResponse()


@router.get("/me", response_model=UserProfileResponse)
async def get_me(
    claims: Annotated[JwtClaims, Depends(get_jwt_claims)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserProfileResponse:
    """Signed-in user profile."""

    return await auth_service.get_profile(user_id=claims.user_id)


@router.patch("/me", response_model=UserProfileResponse)
async def update_me(
    body: UpdateProfileRequest,
    claims: Annotated[JwtClaims, Depends(get_jwt_claims)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserProfileResponse:
    """Update signed-in user profile."""

    return await auth_service.update_profile(user_id=claims.user_id, request=body)


@router.post("/change-password", response_model=AuthMessageResponse)
async def change_password(
    body: ChangePasswordRequest,
    claims: Annotated[JwtClaims, Depends(get_jwt_claims)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> AuthMessageResponse:
    """Change password for the signed-in user."""

    return await auth_service.change_password(user_id=claims.user_id, request=body)
