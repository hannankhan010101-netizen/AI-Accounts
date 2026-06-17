"""Seed permission_definitions and backfill role_permissions from JSON."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from app.constants.permission_registry import flatten_matrix_definitions, parse_permission_code  # noqa: E402
from prisma_generated import Prisma  # noqa: E402


async def seed_catalog(db: Prisma) -> int:
    rows = flatten_matrix_definitions()
    count = 0
    for row in rows:
        await db.permissiondefinition.upsert(
            where={"code": row["code"]},
            data={
                "create": {
                    "code": row["code"],
                    "module": row["module"],
                    "resource": row["resource"],
                    "action": row["action"],
                    "label": row["label"],
                    "groupLabel": row.get("groupLabel"),
                    "sortOrder": row["sortOrder"],
                },
                "update": {
                    "module": row["module"],
                    "resource": row["resource"],
                    "action": row["action"],
                    "label": row["label"],
                    "groupLabel": row.get("groupLabel"),
                    "sortOrder": row["sortOrder"],
                },
            },
        )
        count += 1
    return count


async def ensure_code(db: Prisma, code: str) -> None:
    existing = await db.permissiondefinition.find_unique(where={"code": code})
    if existing is not None:
        return
    module, resource, action = parse_permission_code(code)
    await db.permissiondefinition.create(
        data={
            "code": code,
            "module": module,
            "resource": resource,
            "action": action,
            "label": code,
            "groupLabel": module.title(),
            "sortOrder": 9999,
        },
    )


async def backfill_role_permissions(db: Prisma) -> int:
    roles = await db.role.find_many()
    count = 0
    for role in roles:
        perms = role.permissions if isinstance(role.permissions, list) else json.loads(role.permissions or "[]")
        for code in perms:
            code_str = str(code)
            await ensure_code(db, code_str)
            await db.rolepermission.upsert(
                where={
                    "roleId_permissionCode": {
                        "roleId": role.id,
                        "permissionCode": code_str,
                    }
                },
                data={
                    "create": {"roleId": role.id, "permissionCode": code_str, "granted": True},
                    "update": {"granted": True},
                },
            )
            count += 1
    return count


async def main() -> None:
    db = Prisma()
    await db.connect()
    try:
        catalog = await seed_catalog(db)
        backfill = await backfill_role_permissions(db)
        print(f"Seeded {catalog} permission definitions; backfilled {backfill} role grants.")
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
