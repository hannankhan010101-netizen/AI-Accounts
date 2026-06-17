"""Rule-based contextual learning suggestions (AI-ready) — P51."""

from __future__ import annotations

from typing import Any

from app.services.onboarding_release_service import _perm_match


def _tour_status(tours: dict[str, Any], tour_id: str) -> str:
    entry = tours.get(tour_id)
    if not isinstance(entry, dict):
        return "not_started"
    return str(entry.get("status") or "not_started")


def contextual_suggestions(
    *,
    pathname: str,
    user_perms: list[str],
    progress: dict[str, Any],
    persona: str | None,
    releases: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Ranked next-best actions for the AI assistant panel."""

    tours = progress.get("tours") if isinstance(progress.get("tours"), dict) else {}
    suggestions: list[dict[str, Any]] = []
    dismissed = set(progress.get("dismissedHints") or [])

    def add(
        *,
        id: str,
        title: str,
        reason: str,
        score: int,
        tour_id: str | None = None,
        href: str | None = None,
    ) -> None:
        if id in dismissed:
            return
        suggestions.append(
            {
                "id": id,
                "title": title,
                "reason": reason,
                "score": score,
                "tourId": tour_id,
                "href": href,
            }
        )

    if _tour_status(tours, "onboard.core") != "completed":
        add(
            id="ai.welcome",
            title="Finish workspace orientation",
            reason="You have not completed the welcome tour yet.",
            score=100,
            tour_id="onboard.core",
            href="/dashboard",
        )

    route_hints: list[tuple[str, str, str, str, int]] = [
        ("/sales/invoices", "onboard.sell", "Learn the invoice workflow", "You are on Sales invoices.", 95),
        (
            "/sales/invoices/new",
            "workflow.sales-invoice",
            "Guided invoice form",
            "You are creating a sales invoice.",
            92,
        ),
        (
            "/sales/receipts",
            "workflow.sales-receipt",
            "Record a customer receipt",
            "You are on Sales receipts.",
            91,
        ),
        (
            "/sales/receipts/new",
            "workflow.sales-receipt",
            "Guided customer receipt",
            "You are recording a customer receipt.",
            90,
        ),
        (
            "/purchases/bills/new",
            "workflow.supplier-bill",
            "Guided supplier bill",
            "You are creating a supplier bill.",
            90,
        ),
        (
            "/purchases/payments",
            "workflow.supplier-payment",
            "Pay a supplier bill",
            "You are on Bill payments.",
            89,
        ),
        (
            "/purchases/payments/new",
            "workflow.supplier-payment",
            "Guided supplier payment",
            "You are recording a bill payment.",
            88,
        ),
        ("/bank/balances", "onboard.money", "Set up bank accounts", "You are in Money.", 90),
        ("/bank/reconciliation", "release.bank-recon", "Try complete reconciliation", "Reconciliation saves month-end time.", 88),
        ("/purchases/bills", "onboard.buy", "Learn supplier bills", "You are on Purchase bills.", 85),
        ("/settings/users", "onboard.admin", "Manage team access", "You are on Users settings.", 80),
        ("/inventory/products", "onboard.stock", "Learn the product catalog", "You are on Products.", 82),
        ("/reports", "onboard.reports", "Explore the reports hub", "You are in Insights.", 78),
        (
            "/settings/journals/new",
            "workflow.journal",
            "Guided journal entry",
            "You are posting a manual journal.",
            88,
        ),
        (
            "/bank/receipts/new",
            "workflow.bank-receipt",
            "Guided bank receipt",
            "You are recording a bank receipt.",
            86,
        ),
        (
            "/bank/payments/new",
            "workflow.bank-payment",
            "Guided bank payment",
            "You are recording a payment out.",
            84,
        ),
    ]
    for prefix, tour_id, title, reason, base in route_hints:
        if pathname.startswith(prefix) and _tour_status(tours, tour_id) != "completed":
            add(id=f"ai.route.{tour_id}", title=title, reason=reason, score=base + 10, tour_id=tour_id, href=prefix)

    for release in releases[:3]:
        rid = release.get("id")
        if not rid:
            continue
        add(
            id=f"ai.release.{rid}",
            title=str(release.get("title") or "New feature"),
            reason=str(release.get("summary") or "Recent product update"),
            score=75,
            tour_id=release.get("tourId"),
            href=release.get("href"),
        )

    role = (persona or "").lower()
    if "admin" in role and _tour_status(tours, "onboard.admin") != "completed":
        if any(_perm_match(user_perms, p) for p in ("settings.users.invite", "settings.*", "*")):
            add(
                id="ai.admin",
                title="Invite teammates",
                reason="Admins usually set up users and roles early.",
                score=70,
                tour_id="onboard.admin",
                href="/settings/users",
            )

    if progress.get("maturityScore", 0) < 40:
        add(
            id="ai.maturity",
            title="Build your learning path",
            reason="Low maturity score — complete one module tour next.",
            score=60,
            href="/dashboard",
        )

    suggestions.sort(key=lambda x: int(x.get("score") or 0), reverse=True)
    return suggestions[:6]
