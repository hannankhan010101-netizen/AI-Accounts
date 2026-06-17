"""Advance users visibility filtering."""

from app.services.advance_users_service import AdvanceUsersService


class _Row:
    def __init__(self, id: str, code: str) -> None:
        self.id = id
        self.code = code


class _SettingsStub:
    def __init__(self, rules: list[dict]) -> None:
        self._rules = rules

    async def get_advance_users_settings(self, *, company_id: str) -> dict:
        return {"rules": self._rules}


def test_no_rule_returns_all_rows() -> None:
    svc = AdvanceUsersService(
        app_settings=_SettingsStub([]),  # type: ignore[arg-type]
        prisma_client=None,  # type: ignore[arg-type]
        access_control=None,  # type: ignore[arg-type]
    )
    rows = [_Row("c1", "C001"), _Row("c2", "C002")]
    out = svc._filter_rows(rows, None, id_getter=lambda r: r.id, code_getter=lambda r: r.code)
    assert len(out) == 2


def test_rule_filters_by_id_and_code() -> None:
    svc = AdvanceUsersService(
        app_settings=_SettingsStub([]),  # type: ignore[arg-type]
        prisma_client=None,  # type: ignore[arg-type]
        access_control=None,  # type: ignore[arg-type]
    )
    rows = [_Row("c1", "C001"), _Row("c2", "C002"), _Row("c3", "C003")]
    allowed = {"C002", "c3"}
    out = svc._filter_rows(
        rows, allowed, id_getter=lambda r: r.id, code_getter=lambda r: r.code
    )
    assert [r.code for r in out] == ["C002", "C003"]
