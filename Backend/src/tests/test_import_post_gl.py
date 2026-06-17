"""Import job GL post flags."""

from app.services.import_handlers import (
    _group_wants_post,
    _import_post_gl_enabled,
    _row_wants_post,
)


def test_import_post_gl_enabled_from_options() -> None:
    assert _import_post_gl_enabled({"postGl": True})
    assert _import_post_gl_enabled({"post_gl": True})
    assert not _import_post_gl_enabled({})


def test_row_wants_post_from_status() -> None:
    opts: dict = {}
    assert _row_wants_post({"status": "posted"}, options=opts)
    assert not _row_wants_post({"status": "draft"}, options=opts)
    assert _row_wants_post({"status": "draft"}, options={"postGl": True})


def test_group_wants_post() -> None:
    rows = [(1, {"status": "draft"}), (2, {"status": "posted"})]
    assert _group_wants_post(rows, options={})
    assert not _group_wants_post([(1, {"status": "draft"})], options={})
