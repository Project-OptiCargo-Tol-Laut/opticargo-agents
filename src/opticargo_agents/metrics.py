from __future__ import annotations

from collections import Counter
from threading import Lock


class InMemoryMetrics:
    def __init__(self) -> None:
        self._lock = Lock()
        self._counters: Counter[str] = Counter()

    def inc(self, name: str, amount: int = 1) -> None:
        with self._lock:
            self._counters[name] += amount

    def snapshot(self) -> dict[str, int]:
        with self._lock:
            return dict(self._counters)


METRICS = InMemoryMetrics()


def record_node(node: str, status: str) -> None:
    METRICS.inc(f"node.{node}.{status}")


def record_dependency(name: str, status: str) -> None:
    METRICS.inc(f"dependency.{name}.{status}")


def prometheus_text() -> str:
    """Render the bounded in-memory counters for the internal scrape endpoint."""
    # Keep the exposition compatible with basic Prometheus/Grafana probes even
    # when the optional prometheus_client package is not installed.
    lines = [
        "# HELP python_info Python runtime is available.",
        "# TYPE python_info gauge",
        'python_info{implementation="python"} 1',
        "# HELP opticargo_agents_events_total Agent event counters.",
        "# TYPE opticargo_agents_events_total counter",
    ]
    for name, value in sorted(METRICS.snapshot().items()):
        metric_name = "opticargo_agents_" + name.replace(".", "_") + "_total"
        lines.append(f"{metric_name} {value}")
    return "\n".join(lines) + "\n"


__all__ = ["InMemoryMetrics", "METRICS", "prometheus_text", "record_dependency", "record_node"]
