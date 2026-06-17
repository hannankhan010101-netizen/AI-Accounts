"""Authentication responses beyond token pairs."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SignUpPendingResponse(BaseModel):
    """Returned after registration until email OTP is verified."""

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)

    message: str = "Verification code sent to your email. Complete verification to sign in."
    email: str
    expires_at: datetime = Field(..., serialization_alias="expiresAt")
    dev_otp: str | None = Field(
        default=None,
        serialization_alias="devOtp",
        description="Only present when AUTH_EXPOSE_OTP_IN_RESPONSE is enabled.",
    )


class AuthMessageResponse(BaseModel):
    """Generic auth flow acknowledgement (no sensitive hints)."""

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)

    message: str


class LogoutResponse(BaseModel):
    """Logout acknowledgement."""

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)

    message: str = "Signed out. Discard client tokens."


class UserProfileResponse(BaseModel):
    """Signed-in user profile."""

    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)

    id: str
    email: str
    first_name: str = Field(..., serialization_alias="firstName")
    last_name: str = Field(..., serialization_alias="lastName")
    phone: str | None = None
    email_verified: bool = Field(..., serialization_alias="emailVerified")
