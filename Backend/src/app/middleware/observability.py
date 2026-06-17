"""Request tracing and metrics middleware (Phase 4)."""

from __future__ import annotations

import time
import uuid

from fastapi import Request

from app.core.config import get_settings
from app.core.metrics import get_metrics
from app.core.tracing import get_tracer


async def observability_middleware(request: Request, call_next):
    settings = get_settings()
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    traceparent = request.headers.get("traceparent")
    if traceparent:
        request.state.traceparent = traceparent

    started = time.perf_counter()
    status_code = 500
    response = None
    tracer = get_tracer()
    span_ctx = (
        tracer.start_as_current_span(
            f"{request.method} {request.url.path}",
            attributes={"http.method": request.method, "http.route": request.url.path},
        )
        if tracer
        else None
    )
    try:
        if span_ctx is not None:
            with span_ctx:
                response = await call_next(request)
        else:
            response = await call_next(request)
        status_code = response.status_code
        response.headers["X-Request-ID"] = request_id
        if traceparent := getattr(request.state, "traceparent", None):
            response.headers["traceparent"] = traceparent
        return response
    except Exception:
        raise
    finally:
        elapsed_ms = (time.perf_counter() - started) * 1000
        path = request.url.path
        method = request.method
        metrics = get_metrics()
        metrics.inc(
            "http_requests_total",
            labels={"method": method, "status": str(status_code)},
        )
        metrics.observe(
            "http_request_duration_ms",
            elapsed_ms,
            method=method,
        )
        slow_ms = float(getattr(settings, "slow_request_ms", 500) or 500)
        if elapsed_ms > slow_ms:
            import logging

            logging.getLogger(__name__).warning(
                "Slow request %s %s %.0fms request_id=%s",
                method,
                path,
                elapsed_ms,
                request_id,
            )
