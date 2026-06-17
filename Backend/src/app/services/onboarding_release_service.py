"""Release feed filtering and company onboarding insights — P50."""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.constants.onboarding_releases import RELEASE_CATALOG


def _perm_match(user_perms: list[str], code: str) -> bool:
    if "*" in user_perms or code in user_perms:
        return True
    parts = code.split(".")
    for i in range(len(parts), 0, -1):
        wc = ".".join(parts[:i]) + ".*"
        if wc in user_perms:
            return True
    return False


def _catalog_item_dict(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item["id"],
        "version": item["version"],
        "title": item["title"],
        "summary": item["summary"],
        "publishedAt": item["publishedAt"],
        "tourId": item.get("tourId"),
        "href": item.get("href"),
        "source": "platform",
    }


def releases_for_user(
    user_perms: list[str],
    tenant_items: list[dict[str, Any]] | None = None,
    platform_items: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Platform DB + catalog + tenant CMS (tenant wins on same id)."""

    by_id: dict[str, dict[str, Any]] = {}

    for row in platform_items or []:
        if not row.get("isActive", True):
            continue
        required = row.get("permissions") or []
        if required and not any(_perm_match(user_perms, str(p)) for p in required):
            continue
        by_id[str(row["id"])] = {
            "id": row["id"],
            "version": row["version"],
            "title": row["title"],
            "summary": row["summary"],
            "publishedAt": row["publishedAt"],
            "tourId": row.get("tourId"),
            "href": row.get("href"),
            "source": "platform",
        }

    for item in RELEASE_CATALOG:
        rid = str(item["id"])
        if rid in by_id:
            continue
        required = item.get("permissions") or ()
        if required and not any(_perm_match(user_perms, str(p)) for p in required):
            continue
        by_id[rid] = _catalog_item_dict(item)

    for row in tenant_items or []:
        if not row.get("isActive", True):
            by_id.pop(str(row.get("id", "")), None)
            continue
        required = row.get("permissions") or []
        if required and not any(_perm_match(user_perms, str(p)) for p in required):
            continue
        by_id[str(row["id"])] = {
            "id": row["id"],
            "version": row["version"],
            "title": row["title"],
            "summary": row["summary"],
            "publishedAt": row["publishedAt"],
            "tourId": row.get("tourId"),
            "href": row.get("href"),
            "source": row.get("source", "tenant"),
        }

    out = list(by_id.values())
    out.sort(key=lambda x: str(x.get("publishedAt") or ""), reverse=True)
    return out


def insights_from_payloads(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate tour analytics from stored event logs."""

    tour_started: Counter[str] = Counter()
    tour_completed: Counter[str] = Counter()
    step_views: Counter[str] = Counter()
    users_with_log = 0

    for payload in payloads:
        log = payload.get("eventLog")
        if not isinstance(log, list) or not log:
            continue
        users_with_log += 1
        for ev in log:
            if not isinstance(ev, dict):
                continue
            event = ev.get("event")
            tour_id = ev.get("tourId")
            if not tour_id:
                continue
            if event == "tour_started":
                tour_started[str(tour_id)] += 1
            elif event == "tour_completed":
                tour_completed[str(tour_id)] += 1
            elif event == "step_viewed":
                step_id = ev.get("stepId") or ev.get("stepIndex")
                if step_id is not None:
                    step_views[f"{tour_id}:{step_id}"] += 1

    completion_rates: list[dict[str, Any]] = []
    for tour_id, started in tour_started.items():
        completed = tour_completed.get(tour_id, 0)
        rate = round((completed / started) * 100) if started else 0
        completion_rates.append(
            {"tourId": tour_id, "started": started, "completed": completed, "ratePercent": rate}
        )
    completion_rates.sort(key=lambda x: x["started"], reverse=True)

    drop_offs = [
        {"step": step, "views": count}
        for step, count in step_views.most_common(10)
    ]

    return {
        "usersWithActivity": users_with_log,
        "totalLearners": len(payloads),
        "tourCompletion": completion_rates,
        "topStepViews": drop_offs,
    }
