"""In-app and email notifications for batch expiry alerts."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from app.constants.inventory_alerts import (
    EXPIRY_STATUS_EXPIRED,
    EXPIRY_STATUS_EXPIRING_SOON,
)
from app.repositories.inventory_repository import ProductBatchRepository
from app.repositories.smart_settings_repository import SmartSettingsRepository
from app.services.batch_expiry_alert_service import BatchExpiryAlertService
from app.services.email_service import EmailService
from app.services.smart_settings_runtime import SmartSettingsRuntime


def _notification_id(*, company_id: str, batch_id: str, kind: str) -> str:
    return f"expiry:{company_id}:{batch_id}:{kind}"


async def list_expiry_notifications(
    *,
    company_id: str,
    batch_repo: ProductBatchRepository,
    smart_runtime: SmartSettingsRuntime,
) -> list[dict[str, Any]]:
    """Build ephemeral notification items from current batch expiry state."""

    config = await smart_runtime.inventory_alerts_config(company_id=company_id)
    if not config.get("enabled", True):
        return []

    svc = BatchExpiryAlertService(window_days=int(config["windowDays"]))
    rows = await batch_repo.list_expiring_batches(
        company_id=company_id,
        within_days=int(config["windowDays"]),
    )
    now = datetime.now(UTC)
    notifications: list[dict[str, Any]] = []

    for row in rows:
        enriched = svc.enrich_row(row, now=now)
        status = enriched.get("expiryStatus")
        if status not in (EXPIRY_STATUS_EXPIRED, EXPIRY_STATUS_EXPIRING_SOON):
            continue
        severity = "critical" if status == EXPIRY_STATUS_EXPIRED else "warn"
        days = enriched.get("daysToExpiry")
        if status == EXPIRY_STATUS_EXPIRED:
            message = f"Batch {row.batchNumber} for {row.productCode} has expired."
        elif days == 0:
            message = f"Batch {row.batchNumber} for {row.productCode} expires today."
        else:
            message = (
                f"Batch {row.batchNumber} for {row.productCode} expires in {days} day(s)."
            )
        notifications.append(
            {
                "id": _notification_id(
                    company_id=company_id,
                    batch_id=row.id,
                    kind=status,
                ),
                "type": "batch_expiry",
                "severity": severity,
                "title": "Expired batch" if status == EXPIRY_STATUS_EXPIRED else "Batch expiring soon",
                "message": message,
                "href": "/inventory/batches?filter=expiring",
                "createdAt": now.isoformat(),
                "read": False,
                "productCode": row.productCode,
                "batchNumber": row.batchNumber,
                "expiryDate": row.expiryDate.isoformat() if row.expiryDate else None,
            }
        )

    notifications.sort(
        key=lambda n: (0 if n["severity"] == "critical" else 1, n.get("expiryDate") or ""),
    )
    return notifications


async def send_expiry_digest_if_due(
    *,
    company_id: str,
    company_name: str,
    to_email: str,
    user_name: str,
    batch_repo: ProductBatchRepository,
    smart_runtime: SmartSettingsRuntime,
    smart_repo: SmartSettingsRepository,
    email_service: EmailService,
    app_base_url: str,
) -> tuple[bool, str]:
    """Send one digest email per company when enabled and batches are alertable."""

    config = await smart_runtime.inventory_alerts_config(company_id=company_id)
    if not config.get("enabled", True):
        return False, "Batch expiry alerts are disabled."
    if not config.get("emailDigestEnabled"):
        return False, "Email digest is not enabled."
    if not email_service.is_configured():
        return False, "Email is not configured on this server."

    last_sent_raw = config.get("lastDigestSentAt")
    if last_sent_raw:
        try:
            last_sent = datetime.fromisoformat(str(last_sent_raw).replace("Z", "+00:00"))
            if last_sent.tzinfo is None:
                last_sent = last_sent.replace(tzinfo=UTC)
            if datetime.now(UTC) - last_sent < timedelta(hours=24):
                return False, "Digest already sent within the last 24 hours."
        except ValueError:
            pass

    notifications = await list_expiry_notifications(
        company_id=company_id,
        batch_repo=batch_repo,
        smart_runtime=smart_runtime,
    )
    if not notifications:
        return False, "No expiring batches to report."

    lines = [f"- {n['message']}" for n in notifications[:25]]
    subject = f"[{company_name}] {len(notifications)} batch expiry alert(s)"
    text = (
        f"Hello {user_name},\n\n"
        f"The following batches need attention at {company_name}:\n\n"
        + "\n".join(lines)
        + f"\n\nReview: {app_base_url.rstrip('/')}/inventory/batches?filter=expiring\n"
    )
    html = (
        f"<p>Hello {user_name},</p>"
        f"<p>The following batches need attention at <strong>{company_name}</strong>:</p>"
        "<ul>"
        + "".join(f"<li>{n['message']}</li>" for n in notifications[:25])
        + "</ul>"
        f'<p><a href="{app_base_url.rstrip("/")}/inventory/batches?filter=expiring">'
        "Review batches</a></p>"
    )
    ok = await email_service.send_transactional_email(
        to=to_email,
        subject=subject,
        text=text,
        html=html,
    )
    if not ok:
        return False, "Failed to send email."

    inv = {
        "enabled": config.get("enabled", True),
        "windowDays": config.get("windowDays"),
        "emailDigestEnabled": config.get("emailDigestEnabled"),
        "lastDigestSentAt": datetime.now(UTC).isoformat(),
    }
    existing = await smart_runtime.payload(company_id=company_id)
    prior = existing.get("inventoryAlerts")
    if isinstance(prior, dict):
        inv = {**prior, **inv}
    await smart_repo.merge_payload(company_id=company_id, patch={"inventoryAlerts": inv})
    return True, f"Sent digest with {len(notifications)} alert(s) to {to_email}."
