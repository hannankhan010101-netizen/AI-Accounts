"""RBAC-related audit log transaction types — P31 / RBAC v2."""

from __future__ import annotations

RBAC_AUDIT_TYPES: frozenset[str] = frozenset(
    {
        "USER_INVITE",
        "USER_INVITE_RESEND",
        "USER_MEMBERSHIP_REVOKE",
        "USER_DEACTIVATE",
        "USER_REACTIVATE",
        "USER_REINVITE",
        "USER_BULK_REVOKE",
        "USER_BULK_ASSIGN_ROLE",
        "USER_ROLE_ASSIGN",
        "USER_ROLE_REVOKE",
        "ROLE_CREATE",
        "ROLE_UPDATE",
        "ROLE_DELETE",
        "ROLE_PERMISSION_CHANGE",
        "ROLE_IMPORT_JOB",
        "ROLE_CLONE",
        "ROLE_CLONE_BATCH",
        "ROLE_IMPORT",
        "MODULE_CONFIG_CHANGE",
        "FIELD_POLICY_CHANGE",
        "DATA_SCOPE_CHANGE",
        "APPROVAL_POLICY_CHANGE",
    }
)

RBAC_AUDIT_TYPES_SORTED: tuple[str, ...] = tuple(sorted(RBAC_AUDIT_TYPES))
