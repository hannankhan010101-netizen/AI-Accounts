"""External subscription billing stub — P12.

Syncs ``SubscriptionRecord`` and applies ``planCode`` → module entitlements.
Wire a real provider (Stripe, etc.) by replacing ``apply_webhook_event``.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from app.constants.module_codes import ALL_MODULE_CODES
from app.core.config import get_settings
from app.constants.module_permission_matrix import PLAN_MODULE_DEFAULTS, PLAN_SEAT_LIMITS
from app.services.billing_readiness_service import build_billing_readiness
from app.services.module_entitlement_service import ModuleEntitlementService
from prisma_generated import Prisma


class SubscriptionBillingService:
    def __init__(
        self,
        *,
        prisma: Prisma,
        module_service: ModuleEntitlementService,
    ) -> None:
        self._db = prisma
        self._modules = module_service

    async def get_status(self, *, company_id: str) -> dict[str, Any]:
        row = await self._db.subscriptionrecord.find_unique(
            where={"companyId": company_id}
        )
        entitlements = await self._modules.list_entitlements(company_id=company_id)
        plan_code = row.planCode if row else "standard"
        seats = await self._seat_usage(company_id=company_id, plan_code=plan_code)
        billing = build_billing_readiness(get_settings())
        if row is None:
            return {
                "planCode": "standard",
                "status": "active",
                "externalCustomerId": None,
                "currentPeriodEnd": None,
                "entitlements": entitlements,
                "seats": seats,
                "billing": billing,
            }
        return {
            "planCode": row.planCode,
            "status": row.status,
            "externalCustomerId": row.externalCustomerId,
            "currentPeriodEnd": row.currentPeriodEnd.isoformat()
            if row.currentPeriodEnd
            else None,
            "metadata": row.metadata,
            "entitlements": entitlements,
            "seats": seats,
            "billing": billing,
        }

    async def assert_can_add_member(self, *, company_id: str) -> None:
        """Raise ``ValueError`` when the company is at its plan seat limit."""

        row = await self._db.subscriptionrecord.find_unique(
            where={"companyId": company_id}
        )
        plan_code = row.planCode if row else "standard"
        seats = await self._seat_usage(company_id=company_id, plan_code=plan_code)
        if seats["atLimit"]:
            limit = seats["limit"]
            used = seats["used"]
            raise ValueError(
                f"Seat limit reached ({used}/{limit}) for plan '{plan_code}'"
            )

    async def _seat_usage(
        self, *, company_id: str, plan_code: str
    ) -> dict[str, Any]:
        used = await self._db.companymembership.count(where={"companyId": company_id})
        plan = (plan_code or "standard").strip().lower()
        limit = PLAN_SEAT_LIMITS.get(plan, PLAN_SEAT_LIMITS["standard"])
        if limit is None:
            return {
                "used": used,
                "limit": None,
                "remaining": None,
                "atLimit": False,
            }
        remaining = max(0, limit - used)
        return {
            "used": used,
            "limit": limit,
            "remaining": remaining,
            "atLimit": used >= limit,
        }

    async def apply_webhook_event(
        self,
        *,
        company_id: str,
        event_type: str,
        plan_code: str | None = None,
        external_customer_id: str | None = None,
        period_end: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        plan = (plan_code or "standard").strip().lower()
        status = "active"
        if event_type in {"subscription.cancelled", "customer.subscription.deleted"}:
            status = "cancelled"
        elif event_type in {"invoice.payment_failed"}:
            status = "past_due"

        await self._db.subscriptionrecord.upsert(
            where={"companyId": company_id},
            data={
                "create": {
                    "companyId": company_id,
                    "planCode": plan,
                    "externalCustomerId": external_customer_id,
                    "status": status,
                    "currentPeriodEnd": period_end,
                    "metadata": metadata or {},
                },
                "update": {
                    "planCode": plan,
                    "externalCustomerId": external_customer_id,
                    "status": status,
                    "currentPeriodEnd": period_end,
                    "metadata": metadata or {},
                },
            },
        )

        if status == "active":
            await self._sync_plan_modules(company_id=company_id, plan_code=plan)
        elif status == "cancelled":
            await self._sync_plan_modules(company_id=company_id, plan_code="cancelled")
        elif status == "past_due":
            await self._sync_plan_modules(company_id=company_id, plan_code="past_due")
        return await self.get_status(company_id=company_id)

    async def resolve_company_by_stripe_customer(
        self, *, external_customer_id: str
    ) -> str | None:
        row = await self._db.subscriptionrecord.find_first(
            where={"externalCustomerId": external_customer_id}
        )
        return row.companyId if row else None

    async def _fetch_stripe_subscription_period_end(
        self, *, subscription_id: str
    ) -> datetime | None:
        """Load ``current_period_end`` from Stripe API — P17."""

        settings = get_settings()
        secret = (settings.stripe_secret_key or "").strip()
        if not secret or not subscription_id:
            return None
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"https://api.stripe.com/v1/subscriptions/{subscription_id}",
                auth=(secret, ""),
            )
        if resp.status_code >= 400:
            return None
        payload = resp.json()
        unix_end = payload.get("current_period_end")
        if unix_end is None:
            return None
        return datetime.fromtimestamp(int(unix_end), tz=timezone.utc)

    async def apply_checkout_completed(
        self,
        *,
        company_id: str,
        plan_code: str | None = None,
        external_customer_id: str | None = None,
        subscription_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Persist Stripe customer + subscription period after Checkout — P16/P17."""

        meta = dict(metadata or {})
        if external_customer_id:
            meta["stripeCustomerId"] = external_customer_id
        if subscription_id:
            meta["stripeSubscriptionId"] = subscription_id
        period_end = None
        if subscription_id:
            period_end = await self._fetch_stripe_subscription_period_end(
                subscription_id=subscription_id
            )
        return await self.apply_webhook_event(
            company_id=company_id,
            event_type="checkout.session.completed",
            plan_code=plan_code,
            external_customer_id=external_customer_id,
            period_end=period_end,
            metadata=meta,
        )

    async def create_checkout_session(
        self,
        *,
        company_id: str,
        plan_code: str,
        success_url: str | None = None,
        cancel_url: str | None = None,
    ) -> dict[str, Any]:
        """Create a Stripe Checkout session, or a dev stub when no API key is set — P14."""

        settings = get_settings()
        plan = (plan_code or "starter").strip().lower()
        base = (settings.app_public_url or "http://localhost:3000").rstrip("/")
        success = success_url or f"{base}/settings/module-subscriptions?checkout=success"
        cancel = cancel_url or f"{base}/settings/module-subscriptions?checkout=cancel"
        price_map = {
            "starter": (settings.stripe_price_starter or "").strip(),
            "pro": (settings.stripe_price_pro or "").strip(),
        }
        price_id = price_map.get(plan) or price_map.get("starter", "")

        secret = (settings.stripe_secret_key or "").strip()
        if not secret:
            return {
                "mode": "stub",
                "sessionId": f"stub_cs_{company_id}_{plan}",
                "url": success,
                "planCode": plan,
            }

        if not price_id:
            return {
                "mode": "stub",
                "sessionId": f"stub_cs_{company_id}_{plan}",
                "url": success,
                "planCode": plan,
                "warning": f"No Stripe price configured for plan '{plan}'",
            }

        data = {
            "mode": "subscription",
            "success_url": success,
            "cancel_url": cancel,
            "metadata[company_id]": company_id,
            "metadata[plan_code]": plan,
            "line_items[0][price]": price_id,
            "line_items[0][quantity]": "1",
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.stripe.com/v1/checkout/sessions",
                auth=(secret, ""),
                data=data,
            )
        if resp.status_code >= 400:
            detail = resp.text[:500]
            raise ValueError(f"Stripe checkout failed ({resp.status_code}): {detail}")
        payload = resp.json()
        return {
            "mode": "stripe",
            "sessionId": payload.get("id"),
            "url": payload.get("url"),
            "planCode": plan,
        }

    async def create_portal_session(
        self,
        *,
        company_id: str,
        return_url: str | None = None,
    ) -> dict[str, Any]:
        """Stripe Customer Portal session, or dev stub when not configured — P15."""

        settings = get_settings()
        base = (settings.app_public_url or "http://localhost:3000").rstrip("/")
        ret = return_url or f"{base}/settings/module-subscriptions"

        row = await self._db.subscriptionrecord.find_unique(
            where={"companyId": company_id}
        )
        customer_id = (row.externalCustomerId if row else None) or ""
        customer_id = customer_id.strip()

        secret = (settings.stripe_secret_key or "").strip()
        if not secret or not customer_id:
            return {
                "mode": "stub",
                "sessionId": f"stub_portal_{company_id}",
                "url": ret,
                "warning": None
                if customer_id
                else "No Stripe customer on file — complete checkout first",
            }

        data = {"customer": customer_id, "return_url": ret}
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.stripe.com/v1/billing_portal/sessions",
                auth=(secret, ""),
                data=data,
            )
        if resp.status_code >= 400:
            detail = resp.text[:500]
            raise ValueError(f"Stripe portal failed ({resp.status_code}): {detail}")
        payload = resp.json()
        return {
            "mode": "stripe",
            "sessionId": payload.get("id"),
            "url": payload.get("url"),
        }

    async def _sync_plan_modules(self, *, company_id: str, plan_code: str) -> None:
        enabled_set = PLAN_MODULE_DEFAULTS.get(plan_code, PLAN_MODULE_DEFAULTS["standard"])
        payload = [
            {"moduleCode": code, "enabled": code in enabled_set}
            for code in sorted(ALL_MODULE_CODES)
        ]
        await self._modules.replace_entitlements(
            company_id=company_id, entitlements=payload
        )

    async def apply_stripe_event(
        self,
        *,
        company_id: str,
        event_type: str,
        plan_code: str | None = None,
        external_customer_id: str | None = None,
        period_end_unix: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        period_end = None
        if period_end_unix:
            period_end = datetime.fromtimestamp(period_end_unix, tz=timezone.utc)
        mapped_type = event_type
        if event_type.startswith("customer.subscription.deleted"):
            mapped_type = "customer.subscription.deleted"
        elif event_type.startswith("invoice.payment_failed"):
            mapped_type = "invoice.payment_failed"
        elif event_type.startswith("customer.subscription."):
            mapped_type = "subscription.updated"
        return await self.apply_webhook_event(
            company_id=company_id,
            event_type=mapped_type,
            plan_code=plan_code,
            external_customer_id=external_customer_id,
            period_end=period_end,
            metadata=metadata,
        )
