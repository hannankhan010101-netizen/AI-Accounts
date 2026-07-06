"""Onboarding: default chart of accounts + Smart Settings posting defaults."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.constants.default_chart_of_accounts import (
    DEFAULT_CHART,
    DEFAULT_POSTING_DEFAULTS,
)
from app.repositories.company_bootstrap_repository import CompanyBootstrapRepository
from app.repositories.coa_repository import CoaRepository


def _fake_db_for_seed() -> AsyncMock:
    db = AsyncMock()
    db.coacategory.count.return_value = 0
    db.coacategory.create.return_value = SimpleNamespace(id="cat")
    db.coasection.create.return_value = SimpleNamespace(id="sec")
    db.nominalaccount.create.return_value = SimpleNamespace(id="nom")
    return db


def test_default_posting_defaults_reference_real_chart_codes() -> None:
    # Every code the posting defaults point at must exist in the seeded chart.
    chart_codes = {
        nom["code"]
        for cat in DEFAULT_CHART
        for sec in cat["sections"]
        for nom in sec["nominals"]
    }
    for key, code in DEFAULT_POSTING_DEFAULTS.items():
        assert code in chart_codes, f"{key} -> {code} missing from chart"


@pytest.mark.asyncio
async def test_seed_default_chart_creates_full_tree_when_empty() -> None:
    db = _fake_db_for_seed()
    repo = CoaRepository(db)

    seeded = await repo.seed_default_chart(company_id="c1")

    assert seeded is True
    assert db.coacategory.create.await_count == len(DEFAULT_CHART)
    assert db.coasection.create.await_count == sum(
        len(c["sections"]) for c in DEFAULT_CHART
    )
    assert db.nominalaccount.create.await_count == sum(
        len(s["nominals"]) for c in DEFAULT_CHART for s in c["sections"]
    )


@pytest.mark.asyncio
async def test_seed_default_chart_is_idempotent() -> None:
    db = _fake_db_for_seed()
    db.coacategory.count.return_value = 5  # chart already present
    repo = CoaRepository(db)

    seeded = await repo.seed_default_chart(company_id="c1")

    assert seeded is False
    db.coacategory.create.assert_not_awaited()


def _bootstrap_with_fakes(*, present_codes: set[str], existing_defaults: dict) -> CompanyBootstrapRepository:
    bootstrap = CompanyBootstrapRepository(AsyncMock())
    bootstrap._coa = AsyncMock()
    bootstrap._coa.seed_default_chart.return_value = True
    bootstrap._coa.nominal_ids_by_codes.return_value = {c: f"id-{c}" for c in present_codes}
    bootstrap._smart_settings = AsyncMock()
    bootstrap._smart_settings.get_for_company.return_value = SimpleNamespace(
        payload={"defaults": dict(existing_defaults)}
    )
    return bootstrap


@pytest.mark.asyncio
async def test_defaults_fully_wired_for_new_company() -> None:
    bootstrap = _bootstrap_with_fakes(
        present_codes=set(DEFAULT_POSTING_DEFAULTS.values()), existing_defaults={}
    )

    await bootstrap.seed_chart_and_defaults(company_id="c1")

    payload = bootstrap._smart_settings.upsert_payload.await_args.kwargs["payload"]
    assert payload["defaults"]["salesNominalCode"] == "4000"
    assert set(payload["defaults"]) == set(DEFAULT_POSTING_DEFAULTS)


@pytest.mark.asyncio
async def test_defaults_only_wired_for_codes_present_on_chart() -> None:
    # A company with a custom chart that only has 4000 must not be pointed at codes
    # that do not exist.
    bootstrap = _bootstrap_with_fakes(present_codes={"4000"}, existing_defaults={})

    await bootstrap.seed_chart_and_defaults(company_id="c1")

    payload = bootstrap._smart_settings.upsert_payload.await_args.kwargs["payload"]
    assert payload["defaults"] == {"salesNominalCode": "4000"}


@pytest.mark.asyncio
async def test_existing_default_is_never_overwritten() -> None:
    bootstrap = _bootstrap_with_fakes(
        present_codes=set(DEFAULT_POSTING_DEFAULTS.values()),
        existing_defaults={"salesNominalCode": "9999"},
    )

    await bootstrap.seed_chart_and_defaults(company_id="c1")

    payload = bootstrap._smart_settings.upsert_payload.await_args.kwargs["payload"]
    assert payload["defaults"]["salesNominalCode"] == "9999"  # user value preserved


@pytest.mark.asyncio
async def test_create_category_rejects_bad_type() -> None:
    repo = CoaRepository(AsyncMock())
    with pytest.raises(ValueError):
        await repo.create_category(
            company_id="c1", code="9", name="Bad", category_type="Nonsense"
        )
