from __future__ import annotations

from opticargo_agents.contracts import GraphContextRequest, GraphContextResult
from opticargo_agents.integrations import KnowledgeGraphAdapter


def run_graph_analysis_node(
    request: GraphContextRequest,
    adapter: KnowledgeGraphAdapter,
) -> GraphContextResult:
    return adapter.graph_context(request)


__all__ = ["run_graph_analysis_node"]
