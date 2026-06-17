"""Stripe webhook signature verification — P13."""

from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any


class StripeWebhookError(Exception):
    """Invalid or stale Stripe webhook signature."""


def verify_stripe_signature(
    *,
    payload: bytes,
    signature_header: str,
    secret: str,
    tolerance_seconds: int = 300,
) -> None:
    """Validate ``Stripe-Signature`` header (t=…, v1=…)."""

    if not secret.strip():
        raise StripeWebhookError("STRIPE_WEBHOOK_SECRET is not configured")
    if not signature_header:
        raise StripeWebhookError("Missing Stripe-Signature header")

    parts: dict[str, str] = {}
    for piece in signature_header.split(","):
        if "=" in piece:
            key, value = piece.split("=", 1)
            parts[key.strip()] = value.strip()

    timestamp = parts.get("t")
    v1 = parts.get("v1")
    if not timestamp or not v1:
        raise StripeWebhookError("Malformed Stripe-Signature header")

    try:
        ts = int(timestamp)
    except ValueError as exc:
        raise StripeWebhookError("Invalid timestamp in Stripe-Signature") from exc

    if abs(time.time() - ts) > tolerance_seconds:
        raise StripeWebhookError("Stripe webhook timestamp outside tolerance")

    signed_payload = f"{timestamp}.{payload.decode('utf-8')}".encode("utf-8")
    expected = hmac.new(
        secret.encode("utf-8"), signed_payload, hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(expected, v1):
        raise StripeWebhookError("Stripe signature mismatch")


def parse_stripe_subscription_event(body: dict[str, Any]) -> dict[str, Any]:
    """Extract fields for ``SubscriptionBillingService`` from a Stripe event."""

    obj = body.get("data", {}).get("object", {}) if isinstance(body.get("data"), dict) else {}
    metadata = obj.get("metadata") if isinstance(obj.get("metadata"), dict) else {}
    company_id = metadata.get("company_id") or metadata.get("companyId")
    plan_code = metadata.get("plan_code") or metadata.get("planCode")
    customer_id = obj.get("customer")
    period_end = obj.get("current_period_end")
    event_type = str(body.get("type") or "unknown")
    return {
        "kind": "subscription",
        "companyId": company_id,
        "eventType": event_type,
        "planCode": plan_code,
        "externalCustomerId": str(customer_id) if customer_id else None,
        "periodEndUnix": period_end,
        "rawType": event_type,
    }


def parse_stripe_checkout_completed(body: dict[str, Any]) -> dict[str, Any]:
    """Extract checkout.session.completed fields — P16."""

    obj = body.get("data", {}).get("object", {}) if isinstance(body.get("data"), dict) else {}
    metadata = obj.get("metadata") if isinstance(obj.get("metadata"), dict) else {}
    company_id = metadata.get("company_id") or metadata.get("companyId")
    plan_code = metadata.get("plan_code") or metadata.get("planCode")
    customer_id = obj.get("customer")
    return {
        "kind": "checkout",
        "companyId": company_id,
        "eventType": "checkout.session.completed",
        "planCode": plan_code,
        "externalCustomerId": str(customer_id) if customer_id else None,
        "subscriptionId": obj.get("subscription"),
        "rawType": str(body.get("type") or "checkout.session.completed"),
    }


def parse_stripe_invoice_payment_failed(body: dict[str, Any]) -> dict[str, Any]:
    """Extract ``invoice.payment_failed`` — P18."""

    obj = body.get("data", {}).get("object", {}) if isinstance(body.get("data"), dict) else {}
    customer_id = obj.get("customer")
    sub_id = obj.get("subscription")
    metadata: dict[str, Any] = {}
    sub_details = obj.get("subscription_details")
    if isinstance(sub_details, dict) and isinstance(sub_details.get("metadata"), dict):
        metadata = sub_details["metadata"]
    company_id = metadata.get("company_id") or metadata.get("companyId")
    return {
        "kind": "invoice_failed",
        "companyId": company_id,
        "eventType": "invoice.payment_failed",
        "externalCustomerId": str(customer_id) if customer_id else None,
        "subscriptionId": sub_id,
        "rawType": str(body.get("type") or "invoice.payment_failed"),
    }


def parse_stripe_webhook_event(body: dict[str, Any]) -> dict[str, Any]:
    """Route Stripe event payload to the correct parser."""

    event_type = str(body.get("type") or "")
    if event_type == "checkout.session.completed":
        return parse_stripe_checkout_completed(body)
    if event_type == "invoice.payment_failed":
        return parse_stripe_invoice_payment_failed(body)
    return parse_stripe_subscription_event(body)
