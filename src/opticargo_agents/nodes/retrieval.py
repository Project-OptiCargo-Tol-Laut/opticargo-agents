from __future__ import annotations

from opticargo_agents.contracts import RetrievalRequest, RetrievalResult
from opticargo_agents.integrations import RagAdapter


def run_retrieval_node(request: RetrievalRequest, adapter: RagAdapter) -> RetrievalResult:
    return adapter.retrieve(request)


__all__ = ["run_retrieval_node"]
