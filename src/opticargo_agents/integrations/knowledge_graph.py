from __future__ import annotations

from typing import Any, Callable

from opticargo_agents.config import Settings, get_settings
from opticargo_agents.contracts import GraphContextRequest, GraphContextResult, payload_to_dict
from opticargo_agents.errors import DependencyTimeoutError, DependencyUnavailableError, InvalidRequestError

GraphQueryFunc = Callable[..., Any]
SessionFactory = Callable[[], Any]


class KnowledgeGraphAdapter:
    def __init__(
        self,
        settings: Settings | None = None,
        graph_query_func: GraphQueryFunc | None = None,
        session_factory: SessionFactory | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self._graph_query_func = graph_query_func
        self._session_factory = session_factory

    def health(self) -> dict[str, str]:
        if self._graph_query_func is not None:
            return {"name": "knowledge_graph", "status": "ready", "detail": "injected"}
        try:
            self._load_graph_query_func()
        except Exception as exc:  # pragma: no cover - depends on optional package install
            return {"name": "knowledge_graph", "status": "degraded", "detail": exc.__class__.__name__}
        return {"name": "knowledge_graph", "status": "ready", "detail": "package_available"}

    def graph_context(self, request: GraphContextRequest) -> GraphContextResult:
        has_origin_port = bool((request.origin_port or "").strip())
        if request.voyage_id is None and not has_origin_port:
            error = InvalidRequestError(
                "graph_context requires voyage_id or origin_port to bound the query.",
                dependency="knowledge_graph",
            )
            return GraphContextResult(error=error.envelope(), warnings=[str(error)])

        try:
            query_func = self._load_graph_query_func()
            if self._session_factory is None:
                raise DependencyUnavailableError(
                    "Neo4j session factory is not configured.",
                    dependency="knowledge_graph",
                )
            with self._session_factory() as session:
                context = query_func(
                    session,
                    correlation_id=request.correlation_id,
                    voyage_id=request.voyage_id,
                    origin_port=request.origin_port,
                    commodity=request.commodity,
                    limit=request.limit,
                )
            return GraphContextResult(context=payload_to_dict(context))
        except TimeoutError as exc:
            return self._unavailable(DependencyTimeoutError(str(exc), dependency="knowledge_graph"))
        except Exception as exc:
            if hasattr(exc, "envelope"):
                return GraphContextResult(error=exc.envelope(), warnings=[str(exc)])
            return self._unavailable(DependencyUnavailableError(str(exc), dependency="knowledge_graph"))

    def _load_graph_query_func(self) -> GraphQueryFunc:
        if self._graph_query_func is not None:
            return self._graph_query_func
        from opticargo_knowledge_graph.queries.graph_context import find_backhaul_graph_context

        return find_backhaul_graph_context

    def _unavailable(self, error: DependencyUnavailableError | DependencyTimeoutError) -> GraphContextResult:
        return GraphContextResult(error=error.envelope(), warnings=[str(error)])


__all__ = ["KnowledgeGraphAdapter"]