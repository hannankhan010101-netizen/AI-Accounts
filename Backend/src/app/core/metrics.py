"""In-process Prometheus-style metrics with latency percentiles (Phase 4/5)."""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from typing import Any


def _percentile(sorted_values: list[float], pct: float) -> float:
    if not sorted_values:
        return 0.0
    idx = min(int(len(sorted_values) * pct / 100.0), len(sorted_values) - 1)
    return sorted_values[idx]


class MetricsRegistry:
    def __init__(self, *, sample_limit: int = 2000) -> None:
        self._lock = threading.Lock()
        self._sample_limit = sample_limit
        self._counters: dict[str, float] = defaultdict(float)
        self._histogram_sum: dict[str, float] = defaultdict(float)
        self._histogram_count: dict[str, int] = defaultdict(int)
        self._samples: dict[str, deque[float]] = defaultdict(
            lambda: deque(maxlen=sample_limit)
        )

    def inc(self, name: str, value: float = 1.0, **labels: str) -> None:
        key = self._key(name, labels)
        with self._lock:
            self._counters[key] += value

    def observe(self, name: str, value: float, **labels: str) -> None:
        key = self._key(name, labels)
        with self._lock:
            self._histogram_sum[key] += value
            self._histogram_count[key] += 1
            self._samples[key].append(value)

    @staticmethod
    def _key(name: str, labels: dict[str, str]) -> str:
        if not labels:
            return name
        parts = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f"{name}{{{parts}}}"

    def latency_percentiles(self, metric_prefix: str = "http_request_duration_ms") -> dict[str, Any]:
        with self._lock:
            merged: list[float] = []
            for key, samples in self._samples.items():
                if key.startswith(metric_prefix):
                    merged.extend(samples)
        if not merged:
            return {}
        ordered = sorted(merged)
        return {
            "count": len(ordered),
            "p50": round(_percentile(ordered, 50), 2),
            "p95": round(_percentile(ordered, 95), 2),
            "p99": round(_percentile(ordered, 99), 2),
            "max": round(ordered[-1], 2),
        }

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            counters = dict(self._counters)
            histograms = {
                k: {
                    "sum": self._histogram_sum[k],
                    "count": self._histogram_count[k],
                    "avg": (
                        self._histogram_sum[k] / self._histogram_count[k]
                        if self._histogram_count[k]
                        else 0
                    ),
                }
                for k in self._histogram_sum
            }
        # latency_percentiles() re-acquires the (non-reentrant) lock — call it
        # only after releasing, or snapshot() deadlocks.
        return {
            "counters": counters,
            "histograms": histograms,
            "httpLatencyMs": self.latency_percentiles(),
            "collectedAt": time.time(),
        }

    def render_prometheus(self) -> str:
        lines: list[str] = []
        snap = self.snapshot()
        for key, value in snap["counters"].items():
            lines.append(f"{key} {value}")
        for key, hist in snap["histograms"].items():
            if hist["count"]:
                lines.append(f"{key}_sum {hist['sum']}")
                lines.append(f"{key}_count {hist['count']}")
        return "\n".join(lines) + ("\n" if lines else "")


_registry = MetricsRegistry()


def get_metrics() -> MetricsRegistry:
    return _registry


def reset_metrics_for_tests() -> None:
    global _registry
    _registry = MetricsRegistry()
