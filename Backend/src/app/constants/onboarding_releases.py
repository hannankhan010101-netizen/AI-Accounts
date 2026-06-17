"""Curated product release feed for What's New + release tours — P50."""

from __future__ import annotations

from typing import Any

# Permissions optional — empty means all authenticated tenant users.
RELEASE_CATALOG: tuple[dict[str, Any], ...] = (
    {
        "id": "2026-05-invoice-void",
        "version": "1",
        "title": "Void invoices with replacement",
        "summary": "Void posted sales invoices and start a replacement draft in one flow.",
        "publishedAt": "2026-05-22",
        "tourId": "release.invoice-void",
        "href": "/sales/invoices",
        "permissions": ("sales.invoices.create", "sales.invoices.approve", "sales.*"),
    },
    {
        "id": "2026-05-bank-recon-complete",
        "version": "1",
        "title": "Complete bank reconciliation",
        "summary": "Mark reconciliations complete when your statement matches the ledger.",
        "publishedAt": "2026-05-22",
        "tourId": "release.bank-recon",
        "href": "/bank/reconciliation",
        "permissions": ("bank.reconciliation.create", "bank.*"),
    },
    {
        "id": "2026-05-guided-onboarding",
        "version": "1",
        "title": "Guided learning hub",
        "summary": "Compass button tours, resume after refresh, and personalized tips on Home.",
        "publishedAt": "2026-05-23",
        "tourId": "onboard.core",
        "href": "/dashboard",
        "permissions": (),
    },
)
