"""Validate role permission codes against the catalog — P26 / RBAC v2."""

from __future__ import annotations

from app.constants.module_permission_matrix import MODULE_PERMISSION_MATRIX
from app.constants.permission_catalog import flatten_permission_entries
from app.constants.permission_registry import all_known_codes


def known_permission_codes() -> frozenset[str]:
    codes: set[str] = set(all_known_codes())
    codes.update(row["code"] for row in flatten_permission_entries())
    for perms in MODULE_PERMISSION_MATRIX.values():
        codes.update(perms)
    return frozenset(codes)


def validate_role_permissions(permissions: list[str]) -> dict[str, list[str]]:
    """Return unknown codes and human-readable warnings (non-blocking)."""

    known = known_permission_codes()
    unknown = sorted({c for c in permissions if c not in known})
    warnings = [f"Unknown permission code: {c}" for c in unknown]
    return {
        "unknownPermissions": unknown,
        "permissionWarnings": warnings,
    }


def known_codes_sorted() -> list[str]:
    """Flat sorted list for autocomplete — P27."""

    return sorted(known_permission_codes())


def strict_validation_error(validation: dict[str, list[str]]) -> str | None:
    """Message when strict mode should block save; None if allowed."""

    unknown = validation.get("unknownPermissions") or []
    if not unknown:
        return None
    return f"Unknown permission codes: {', '.join(unknown)}"
