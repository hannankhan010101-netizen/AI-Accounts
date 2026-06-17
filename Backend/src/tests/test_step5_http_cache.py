"""Step 5 — HTTP cache headers on reference GET endpoints."""

from __future__ import annotations

from app.core.http_cache import NO_STORE_CACHE_CONTROL, REFERENCE_CACHE_CONTROL
from app.repositories.coa_repository import CoaRepository
from app.services.app_settings_service import AppSettingsService


def test_reference_cache_control_constants() -> None:
    assert "private" in REFERENCE_CACHE_CONTROL
    assert "max-age=300" in REFERENCE_CACHE_CONTROL
    assert "stale-while-revalidate=60" in REFERENCE_CACHE_CONTROL
    assert NO_STORE_CACHE_CONTROL == "private, no-store"


def test_menu_etag_stable() -> None:
    assert AppSettingsService.menu_etag("rev-a") == AppSettingsService.menu_etag("rev-a")
    assert AppSettingsService.menu_etag("rev-a") != AppSettingsService.menu_etag("rev-b")


def test_coa_tree_etag_stable() -> None:
    assert CoaRepository.tree_etag("rev-1") == CoaRepository.tree_etag("rev-1")
    assert CoaRepository.tree_etag("rev-1") != CoaRepository.tree_etag("rev-2")
