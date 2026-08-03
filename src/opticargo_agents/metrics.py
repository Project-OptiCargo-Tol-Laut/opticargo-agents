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


__all__ = ["InMemoryMetrics", "METRICS", "record_dependency", "record_node"]
