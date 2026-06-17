from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.smart_settings_repository import SmartSettingsRepository


@pytest.mark.asyncio
async def test_merge_payload_preserves_existing_keys() -> None:
    db = AsyncMock()
    existing = MagicMock()
    existing.payload = {"others": {"x": 1}, "reportFavorites": ["/reports/trial-balance"]}
    db.smartsettings.find_unique = AsyncMock(return_value=existing)
    db.smartsettings.upsert = AsyncMock(
        return_value=MagicMock(
            payload={"others": {"x": 1}, "reportFavorites": ["/reports/pl", "/reports/bs"]}
        )
    )

    repo = SmartSettingsRepository(db)
    row = await repo.merge_payload(
        company_id="co1",
        patch={"reportFavorites": ["/reports/pl", "/reports/bs"]},
    )

    assert row.payload["others"] == {"x": 1}
    assert row.payload["reportFavorites"] == ["/reports/pl", "/reports/bs"]
    upsert_data = db.smartsettings.upsert.call_args.kwargs["data"]
    assert upsert_data["update"]["payload"]["reportFavorites"] == [
        "/reports/pl",
        "/reports/bs",
    ]
