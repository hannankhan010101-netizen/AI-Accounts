"""Rate limiting for webhooks, auth, assistant, and reports — P9 / Phase 2."""



from __future__ import annotations



import time

from collections import defaultdict

from threading import Lock



from fastapi import Request



from app.core.config import get_settings





class RateLimiter:

    """Token-bucket style limiter keyed by client IP + route group."""



    def __init__(self) -> None:

        self._hits: dict[str, list[float]] = defaultdict(list)

        self._lock = Lock()



    def allow(self, *, key: str, limit: int, window_seconds: int = 60) -> bool:

        if limit <= 0:

            return True

        now = time.monotonic()

        cutoff = now - window_seconds

        with self._lock:

            bucket = [t for t in self._hits[key] if t > cutoff]

            if len(bucket) >= limit:

                self._hits[key] = bucket

                return False

            bucket.append(now)

            self._hits[key] = bucket

            return True



    def clear(self) -> None:

        with self._lock:

            self._hits.clear()





_limiter = RateLimiter()





def _limit_for_group(group: str) -> int:

    settings = get_settings()

    if group == "webhook":

        return settings.rate_limit_webhooks_per_minute

    if group == "auth":

        return settings.rate_limit_auth_per_minute

    if group == "assistant":

        return settings.assistant_rate_limit_per_minute

    if group == "reports":

        return settings.rate_limit_reports_per_minute

    return 0





async def _redis_allow(*, key: str, limit: int, window_seconds: int = 60) -> bool | None:

    from app.core.redis_client import get_redis



    redis = await get_redis()

    if redis is None:

        return None

    bucket = f"ratelimit:{key}"

    count = await redis.incr(bucket)

    if count == 1:

        await redis.expire(bucket, window_seconds)

    return count <= limit





def check_rate_limit(

    request: Request, *, group: str, subject: str | None = None

) -> None:

    """Raise ``PermissionError`` when limit exceeded (in-memory; sync routes)."""



    limit = _limit_for_group(group)

    from app.core.webhook_guard import client_ip



    if subject:

        key = f"{group}:{subject}"

    else:

        ip = client_ip(request) or "unknown"

        key = f"{group}:{ip}"

    if not _limiter.allow(key=key, limit=limit, window_seconds=60):

        raise PermissionError(f"Rate limit exceeded for {group}")





async def check_rate_limit_async(

    request: Request, *, group: str, subject: str | None = None

) -> None:

    """Async rate limit with Redis when ``REDIS_URL`` is configured."""



    limit = _limit_for_group(group)

    from app.core.webhook_guard import client_ip



    if subject:

        key = f"{group}:{subject}"

    else:

        ip = client_ip(request) or "unknown"

        key = f"{group}:{ip}"



    allowed = await _redis_allow(key=key, limit=limit)

    if allowed is None:

        if not _limiter.allow(key=key, limit=limit, window_seconds=60):

            raise PermissionError(f"Rate limit exceeded for {group}")

    elif not allowed:

        raise PermissionError(f"Rate limit exceeded for {group}")





def reset_for_tests() -> None:

    """Clear buckets (tests only)."""



    _limiter.clear()


