"""What's New email digest for learners — P55."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.services.email_service import EmailService
from app.services.onboarding_release_service import releases_for_user


def digest_sent_today(progress: dict[str, Any]) -> bool:
    prefs = progress.get("preferences")
    if not isinstance(prefs, dict):
        return False
    at = prefs.get("lastDigestSentAt")
    if not at or not isinstance(at, str):
        return False
    today = datetime.now(UTC).date().isoformat()
    return at[:10] == today


def digest_is_due(
    progress: dict[str, Any],
    releases: list[dict[str, Any]],
) -> bool:
    prefs = progress.get("preferences")
    if not isinstance(prefs, dict) or not prefs.get("emailDigestEnabled"):
        return False
    if digest_sent_today(progress):
        return False
    return len(unread_releases_for_user(releases, progress)) > 0


def unread_releases_for_user(
    releases: list[dict[str, Any]],
    progress: dict[str, Any],
) -> list[dict[str, Any]]:
    """Same rules as frontend release-feed unread."""

    dismissed = set(progress.get("dismissedHints") or [])
    tours = progress.get("tours") if isinstance(progress.get("tours"), dict) else {}
    out: list[dict[str, Any]] = []
    for r in releases:
        rid = str(r.get("id", ""))
        if not rid:
            continue
        if f"release.{rid}" in dismissed:
            continue
        tour_id = r.get("tourId")
        if tour_id:
            entry = tours.get(str(tour_id))
            if isinstance(entry, dict) and entry.get("status") == "completed":
                if int(entry.get("version") or 0) >= int(r.get("version") or 0):
                    continue
        out.append(r)
    return out


def build_digest_email(
    *,
    user_name: str,
    company_name: str,
    releases: list[dict[str, Any]],
    app_base_url: str,
) -> tuple[str, str, str]:
    subject = f"What's new in Fast Accounts — {len(releases)} update{'s' if len(releases) != 1 else ''}"
    lines_text = []
    lines_html = []
    for r in releases[:8]:
        title = str(r.get("title") or "Update")
        summary = str(r.get("summary") or "")
        href = r.get("href") or "/dashboard"
        url = f"{app_base_url.rstrip('/')}{href}" if href.startswith("/") else href
        lines_text.append(f"- {title}: {summary}")
        lines_html.append(
            f'<li><strong>{title}</strong><br/><span style="color:#555">{summary}</span>'
            f' <a href="{url}">Open</a></li>'
        )
    intro = f"Hi {user_name or 'there'},\n\nHere are product updates for {company_name}:\n\n"
    text = intro + "\n".join(lines_text) + "\n\nOpen the app: " + app_base_url + "\n"
    html = (
        f"<p>Hi {user_name or 'there'},</p>"
        f"<p>Here are product updates for <strong>{company_name}</strong>:</p>"
        f"<ul>{''.join(lines_html)}</ul>"
        f'<p><a href="{app_base_url}">Open Fast Accounts</a></p>'
    )
    return subject, text, html


async def send_whats_new_digest(
    *,
    email_service: EmailService,
    to_email: str,
    user_name: str,
    company_name: str,
    user_perms: list[str],
    progress: dict[str, Any],
    tenant_releases: list[dict[str, Any]] | None,
    platform_releases: list[dict[str, Any]] | None,
    app_base_url: str,
) -> tuple[bool, str]:
    """Send digest if mail is configured and there are unread releases."""

    if not email_service.is_configured():
        return False, "Email is not configured on this server."

    all_releases = releases_for_user(user_perms, tenant_releases, platform_releases)
    unread = unread_releases_for_user(all_releases, progress)
    if not unread:
        return False, "No unread What's New items."

    subject, text, html = build_digest_email(
        user_name=user_name,
        company_name=company_name,
        releases=unread,
        app_base_url=app_base_url,
    )
    ok = await email_service.send_digest_email(
        to=to_email,
        subject=subject,
        text=text,
        html=html,
    )
    if not ok:
        return False, "Failed to send email."
    return True, f"Sent {len(unread)} update(s) to {to_email}."
