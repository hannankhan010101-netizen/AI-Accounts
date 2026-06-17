"""Invite email template request bodies — P30."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class InviteEmailTemplateRequest(BaseModel):
    subject: str | None = Field(default=None, max_length=200)
    intro_text: str | None = Field(default=None, max_length=4000, alias="introText")
    intro_html: str | None = Field(default=None, max_length=8000, alias="introHtml")

    model_config = {"populate_by_name": True}

    def as_dict(self) -> dict[str, str]:
        out: dict[str, str] = {}
        if self.subject is not None:
            out["subject"] = self.subject
        if self.intro_text is not None:
            out["introText"] = self.intro_text
        if self.intro_html is not None:
            out["introHtml"] = self.intro_html
        return out


class InviteEmailPreviewRequest(BaseModel):
    """Render template with sample placeholder values — P39."""

    kind: Literal["invite", "welcome"]
    subject: str | None = Field(default=None, max_length=200)
    intro_text: str | None = Field(default=None, max_length=4000, alias="introText")
    intro_html: str | None = Field(default=None, max_length=8000, alias="introHtml")

    model_config = {"populate_by_name": True}

    def as_dict(self) -> dict[str, str]:
        return InviteEmailTemplateRequest(
            subject=self.subject,
            intro_text=self.intro_text,
            intro_html=self.intro_html,
        ).as_dict()
