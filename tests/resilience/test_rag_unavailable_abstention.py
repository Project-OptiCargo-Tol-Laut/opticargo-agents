from uuid import uuid4

from opticargo_agents.config import load_settings
from opticargo_agents.contracts import AgentRequest
from opticargo_agents.integrations.rag import RagAdapter
from opticargo_agents.orchestrator.graph import WorkflowNodes, WorkflowRunner
from opticargo_agents.orchestrator.service import OrchestrationService
from opticargo_agents.runtime import Runtime


def failing_retrieve(*args, **kwargs):
    raise TimeoutError("Qdrant connection timed out")


def _fake_nodes() -> WorkflowNodes:
    from opticargo_agents.contracts import GraphContextResult, IntentResult
    from opticargo_agents.nodes import run_retrieval_node, run_synthesis_node

    return WorkflowNodes(
        intent=lambda query, requested_intent=None: IntentResult(intent="regulation", confidence=1),
        graph=lambda request, adapter: GraphContextResult(context={}),
        retrieval=run_retrieval_node,
        optimization=lambda payload, client, correlation_id=None: None,
        synthesis=run_synthesis_node,
    )


def test_rag_unavailable_causes_abstention() -> None:
    settings = load_settings({})
    rag = RagAdapter(settings, retrieve_func=failing_retrieve)

    runtime = Runtime(
        settings=settings,
        rag=rag,
        knowledge_graph=None,  # type: ignore
        ml_models=None,  # type: ignore
    )
    runner = WorkflowRunner(runtime=runtime, nodes=_fake_nodes())
    service = OrchestrationService(runner=runner, settings=settings)

    request = AgentRequest(query="aturan terbaru", requested_intent="regulation", correlation_id=uuid4())
    response = service.handle(request)

    assert response.abstained is True
    assert "RAG evidence is unavailable" in str(response.abstention_reason)

    traces = response.trace
    retrieval_trace = next(t for t in traces if t["node"] == "retrieval")
    assert retrieval_trace["status"] == "failed"
    assert "rag evidence is unavailable" in str(retrieval_trace["detail"]).lower()
