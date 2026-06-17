"""Tour / onboarding API bodies — P48."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class OnboardingPreferencesBody(BaseModel):
    """Learning notification preferences — P55/P56."""

    emailDigestEnabled: bool = False
    lastDigestSentAt: str | None = None


class OnboardingProgressBody(BaseModel):
    """Client tour progress document (mirrors frontend UserTourProgress)."""

    tours: dict[str, Any] = Field(default_factory=dict)
    maturityScore: int = 0
    dismissedHints: list[str] = Field(default_factory=list)
    lastActiveTourId: str | None = None
    preferences: OnboardingPreferencesBody | None = None

    def to_payload(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "tours": self.tours,
            "maturityScore": self.maturityScore,
            "dismissedHints": self.dismissedHints,
            "lastActiveTourId": self.lastActiveTourId,
            "eventLog": [],
        }
        if self.preferences is not None:
            out["preferences"] = {
                "emailDigestEnabled": self.preferences.emailDigestEnabled,
                "lastDigestSentAt": self.preferences.lastDigestSentAt,
            }
        return out


class OnboardingEventItem(BaseModel):
    event: str
    tourId: str
    stepId: str | None = None
    stepIndex: int | None = None
    durationMs: int | None = None
    pathname: str | None = None


class OnboardingEventsBody(BaseModel):
    events: list[OnboardingEventItem] = Field(default_factory=list)


class OnboardingAssistantRequest(BaseModel):
    """Learning assistant chat — P52."""

    message: str = Field(min_length=1, max_length=500)
    pathname: str = Field(default="/dashboard", max_length=256)
