"""Authentication request bodies (camelCase JSON)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class SignUpRequest(BaseModel):
    """Register a user and initial company."""

    model_config = {"populate_by_name": True}

    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, alias="firstName")
    last_name: str = Field(..., min_length=1, alias="lastName")
    company_name: str = Field(..., min_length=1, alias="companyName")


class LoginRequest(BaseModel):
    """Password login."""

    model_config = {"populate_by_name": True}

    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """Refresh access token."""

    model_config = {"populate_by_name": True}

    refresh_token: str = Field(..., alias="refreshToken")
    company_id: str | None = Field(default=None, alias="companyId")


class VerifyEmailRequest(BaseModel):
    """Confirm signup email with OTP."""

    model_config = {"populate_by_name": True}

    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6, alias="otpCode", pattern=r"^\d{6}$")


class ResendOtpRequest(BaseModel):
    """Request a new OTP for signup or password reset."""

    model_config = {"populate_by_name": True}

    email: EmailStr
    purpose: Literal["signup", "password_reset"] = Field(..., alias="purpose")


class ForgotPasswordRequest(BaseModel):
    """Start password reset (sends OTP when account exists)."""

    model_config = {"populate_by_name": True}

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Complete password reset or invite setup with email OTP."""

    model_config = {"populate_by_name": True}

    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6, alias="otpCode", pattern=r"^\d{6}$")
    new_password: str = Field(..., min_length=8, alias="newPassword")
    purpose: Literal["password_reset", "user_invite"] = Field(
        default="password_reset",
        description="Use user_invite for invited accounts that are not yet verified",
    )


class CreateCompanyRequest(BaseModel):
    """Create an additional company for the signed-in user."""

    model_config = {"populate_by_name": True}

    name: str = Field(..., min_length=1, max_length=200)


class UpdateProfileRequest(BaseModel):
    """Update signed-in user profile fields."""

    model_config = {"populate_by_name": True}

    first_name: str | None = Field(default=None, min_length=1, alias="firstName")
    last_name: str | None = Field(default=None, min_length=1, alias="lastName")
    phone: str | None = Field(default=None, max_length=32)


class ChangePasswordRequest(BaseModel):
    """Change password for the signed-in user."""

    model_config = {"populate_by_name": True}

    current_password: str = Field(..., min_length=8, alias="currentPassword")
    new_password: str = Field(..., min_length=8, alias="newPassword")
