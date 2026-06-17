"""Async I/O helpers — gather and CPU offload (Step 4)."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

T = TypeVar("T")


async def gather_named(**coros: Awaitable[Any]) -> dict[str, Any]:
    """Run awaitables concurrently; return {name: result}."""

    if not coros:
        return {}
    keys = list(coros.keys())
    results = await asyncio.gather(*coros.values())
    return dict(zip(keys, results))


async def maybe_thread(
    fn: Callable[..., T],
    /,
    *args: Any,
    min_rows: int = 0,
    row_count: int = 0,
    **kwargs: Any,
) -> T:
    """Run ``fn`` in a worker thread when ``row_count`` meets ``min_rows``."""

    if row_count >= min_rows:
        return await asyncio.to_thread(fn, *args, **kwargs)
    return fn(*args, **kwargs)
