"""P13 foundation unit tests."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time

os.environ.setdefault("SKIP_PRISMA", "1")

import pytest

from app.constants.report_aliases import resolve_report_handler_id
from app.constants.report_bank_financial_registry import bank_financial_coverage
from app.core.stripe_webhook import (
    StripeWebhookError,
    parse_stripe_subscription_event,
    verify_stripe_signature,
)


def test_bank_financial_numeric_aliases() -> None:
    assert resolve_report_handler_id("072") == "BANK_REC"
    assert resolve_report_handler_id("073") == "BANK_BAL"
    summary = bank_financial_coverage()
    assert summary["unmappedBankFinancialIds"] == []


def test_stripe_signature_roundtrip() -> None:
    secret = "whsec_test"
    payload = b'{"id":"evt_1"}'
    ts = str(int(time.time()))
    signed = hmac.new(
        secret.encode(),
        f"{ts}.{payload.decode()}".encode(),
        hashlib.sha256,
    ).hexdigest()
    header = f"t={ts},v1={signed}"
    verify_stripe_signature(
        payload=payload, signature_header=header, secret=secret
    )


def test_stripe_signature_rejects_bad_sig() -> None:
    with pytest.raises(StripeWebhookError):
        verify_stripe_signature(
            payload=b"{}",
            signature_header="t=1,v1=bad",
            secret="whsec_test",
        )


def test_parse_stripe_subscription_event() -> None:
    body = {
        "type": "customer.subscription.updated",
        "data": {
            "object": {
                "customer": "cus_123",
                "metadata": {"company_id": "co_1", "plan_code": "starter"},
                "current_period_end": 1893456000,
            }
        },
    }
    parsed = parse_stripe_subscription_event(body)
    assert parsed["companyId"] == "co_1"
    assert parsed["planCode"] == "starter"


def test_fin_cmp_multi_period_handler() -> None:
    import inspect

    from app.services.report_query_service import ReportQueryService

    src = inspect.getsource(ReportQueryService._financial_comparative_pnl)
    assert "period_count" in src.lower() or "periodCount" in src


@pytest.mark.asyncio
async def test_openapi_p13_routes() -> None:
    from app.main import app

    paths = app.openapi()["paths"]
    assert "/api/v1/companies/{company_id}/billing/webhook/stripe" in paths
    assert "/api/v1/companies/{company_id}/reports/comparative-profit-and-loss" in paths
