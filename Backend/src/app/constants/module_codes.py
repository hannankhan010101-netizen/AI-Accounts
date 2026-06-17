"""Licensed module codes for subscription gates — P11."""

from __future__ import annotations

ALL_MODULE_CODES: frozenset[str] = frozenset(
    {
        "sales",
        "purchases",
        "bank",
        "inventory",
        "assembly",
        "projects",
        "financial",
        "fbr",
        "payments",
    }
)

DEFAULT_ENABLED_MODULES: frozenset[str] = ALL_MODULE_CODES
