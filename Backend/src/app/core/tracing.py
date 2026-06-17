"""Optional OpenTelemetry tracing (install with ``pip install -e '.[observability]'``)."""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

_tracer: Any | None = None
_initialized = False


def setup_tracing() -> None:
    """Configure a global tracer when OTLP endpoint is set and SDK is installed."""

    global _tracer, _initialized
    if _initialized:
        return
    _initialized = True

    endpoint = (os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT") or "").strip()
    if not endpoint:
        return
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )
    except ImportError:
        logger.warning(
            "OTEL_EXPORTER_OTLP_ENDPOINT is set but opentelemetry packages are not installed"
        )
        return

    service_name = os.getenv("OTEL_SERVICE_NAME", "fast-accounts-api")
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint))
    )
    trace.set_tracer_provider(provider)
    _tracer = trace.get_tracer(__name__)
    logger.info("OpenTelemetry tracing enabled for %s", service_name)


def get_tracer() -> Any | None:
    return _tracer
