from uuid import uuid4

from opticargo_agents.config import load_settings
from opticargo_agents.contracts import AgentRequest
from opticargo_agents.integrations.knowledge_graph import KnowledgeGraphAdapter
from opticargo_agents.orchestrator.graph import WorkflowNodes, WorkflowRunner
from opticargo_agents.orchestrator.service import OrchestrationService
from opticargo_agents.runtime import Runtime


def failing_graph_query(*args, **kwargs):
    raise ConnectionError("Neo4j is unreachable")


class DummySession:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def _fake_nodes() -> WorkflowNodes:
    from opticargo_agents.contracts import IntentResult, RetrievalResult
    from opticargo_agents.nodes import run_graph_analysis_node, run_synthesis_node

    return WorkflowNodes(
        intent=lambda query, requested_intent=None: IntentResult(intent="route", confidence=1),
        graph=run_graph_analysis_node,
        retrieval=lambda request, adapter: RetrievalResult(query=request.query),
        optimization=lambda payload, client, correlation_id=None: None,
        synthesis=run_synthesis_node,
    )


def test_graph_unavailable_causes_abstention() -> None:
    settings = load_settings({})
    kg = KnowledgeGraphAdapter(
        settings,
        graph_query_func=failing_graph_query,
        session_factory=lambda: DummySession()
    )

    runtime = Runtime(
        settings=settings,
        rag=None,  # type: ignore
        knowledge_graph=kg,
        ml_models=None,  # type: ignore
    )
    runner = WorkflowRunner(runtime=runtime, nodes=_fake_nodes())
    service = OrchestrationService(runner=runner, settings=settings)

    request = AgentRequest(query="rute makassar sorong", requested_intent="route", correlation_id=uuid4(), voyage_id=uuid4())
    response = service.handle(request)

    assert response.abstained is True
    assert "konteks knowledge graph tidak tersedia" in str(response.abstention_reason).lower()

    traces = response.trace
    graph_trace = next(t for t in traces if t["node"] == "graph")
    assert graph_trace["status"] == "failed"
    assert graph_trace["detail"] == "dependency_unavailable"
