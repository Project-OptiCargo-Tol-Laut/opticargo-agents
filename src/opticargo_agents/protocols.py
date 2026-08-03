from __future__ import annotations

from typing import Protocol

from opticargo_agents.contracts import GraphContextRequest, GraphContextResult, RetrievalRequest, RetrievalResult


class GraphProvider(Protocol):
    def graph_context(self, request: GraphContextRequest) -> GraphContextResult:
        ...


class RetrievalProvider(Protocol):
    def retrieve(self, request: RetrievalRequest) -> RetrievalResult:
        ...


class ScoringProvider(Protocol):
    def score_cargo_match(self, payload: dict, *, correlation_id: str | None = None):
        ...


__all__ = ["GraphProvider", "RetrievalProvider", "ScoringProvider"]
