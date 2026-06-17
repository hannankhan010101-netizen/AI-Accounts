"""Release CMS request bodies — P51."""

from __future__ import annotations

from pydantic import BaseModel, Field


class OnboardingReleaseCreateRequest(BaseModel):
    releaseKey: str = Field(min_length=1, max_length=80)
    version: str = "1"
    title: str = Field(min_length=1, max_length=200)
    summary: str = Field(min_length=1, max_length=500)
    publishedAt: str = Field(min_length=4, max_length=32)
    tourId: str | None = None
    href: str | None = None
    permissions: list[str] = Field(default_factory=list)
    isActive: bool = True
    sortOrder: int = 0


class OnboardingReleaseUpdateRequest(BaseModel):
    version: str | None = None
    title: str | None = None
    summary: str | None = None
    publishedAt: str | None = None
    tourId: str | None = None
    href: str | None = None
    permissions: list[str] | None = None
    isActive: bool | None = None
    sortOrder: int | None = None
