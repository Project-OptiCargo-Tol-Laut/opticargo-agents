from opticargo_agents.config import load_settings
from opticargo_agents.contracts import GraphContextRequest
from opticargo_agents.integrations import KnowledgeGraphAdapter


class FakeSession:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


def test_knowledge_graph_adapter_uses_injected_query() -> None:
    def query(session, correlation_id, voyage_id=None, origin_port=None, commodity=None, limit=20):
        return {
            "correlation_id": str(correlation_id),
            "voyage_id": str(voyage_id) if voyage_id else None,
            "candidates": [],
            "warnings": [],
        }

    adapter = KnowledgeGraphAdapter(
        load_settings({}),
        graph_query_func=query,
        session_factory=FakeSession,
    )

    result = adapter.graph_context(GraphContextRequest(origin_port="Makassar"))

    assert result.available is True
    assert result.context["candidates"] == []


def test_knowledge_graph_adapter_returns_typed_failure_without_session() -> None:
    adapter = KnowledgeGraphAdapter(load_settings({}), graph_query_func=lambda **kwargs: {})

    result = adapter.graph_context(GraphContextRequest(origin_port="Makassar"))

    assert result.available is False
    assert result.error is not None
    assert result.error.dependency == "knowledge_graph"
