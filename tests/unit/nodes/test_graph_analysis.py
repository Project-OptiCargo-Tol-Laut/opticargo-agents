from uuid import uuid4

from opticargo_agents.config import load_settings
from opticargo_agents.contracts import GraphContextRequest
from opticargo_agents.integrations import KnowledgeGraphAdapter
from opticargo_agents.nodes.graph_analysis import run_graph_analysis_node


class FakeSession:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


def test_graph_analysis_node_returns_available_context_from_adapter() -> None:
    def query(session, correlation_id, voyage_id=None, origin_port=None, commodity=None, limit=20):
        return {"candidates": [{"supplier_id": "s1"}], "origin_port": origin_port}

    adapter = KnowledgeGraphAdapter(
        load_settings({}),
        graph_query_func=query,
        session_factory=FakeSession,
    )

    result = run_graph_analysis_node(GraphContextRequest(origin_port="Tanjung Perak"), adapter)

    assert result.available is True
    assert result.context["candidates"] == [{"supplier_id": "s1"}]
    assert result.error is None


def test_graph_analysis_node_propagates_degraded_result_when_dependency_unavailable() -> None:
    adapter = KnowledgeGraphAdapter(load_settings({}))

    result = run_graph_analysis_node(GraphContextRequest(voyage_id=uuid4()), adapter)

    assert result.available is False
    assert result.error is not None
    assert result.error.dependency == "knowledge_graph"


def test_graph_analysis_node_propagates_invalid_request_when_unanchored() -> None:
    adapter = KnowledgeGraphAdapter(load_settings({}))

    result = run_graph_analysis_node(GraphContextRequest(), adapter)

    assert result.available is False
    assert result.error is not None
    assert result.error.code == "invalid_request"