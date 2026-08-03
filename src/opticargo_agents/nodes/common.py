from __future__ import annotations

from collections.abc import Callable
from time import perf_counter
from typing import TypeVar

from opticargo_agents.contracts import NodeTrace

T = TypeVar("T")


def timed_node(name: str, fn: Callable[[], T]) -> tuple[T, NodeTrace]:
    started = perf_counter()
    result = fn()
    elapsed_ms = int((perf_counter() - started) * 1000)
    return result, NodeTrace(node=name, status="completed", detail=f"{elapsed_ms}ms")


__all__ = ["timed_node"]
