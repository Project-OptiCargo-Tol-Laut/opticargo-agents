import time
from uuid import uuid4

from opticargo_agents.config import load_settings
from opticargo_agents.contracts import AgentRequest
from opticargo_agents.integrations.rag import RagAdapter
from opticargo_agents.orchestrator.graph import WorkflowNodes, WorkflowRunner
from opticargo_agents.orchestrator.service import OrchestrationService
from opticargo_agents.runtime import Runtime


def slow_retrieve(*args, **kwargs):
    time.sleep(0.2)
    return {"query": "test", "abstained": False}


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


def test_node_timeout_causes_abstention() -> None:
    settings = load_settings({"AGENTS_REQUEST_TIMEOUT_SECONDS": "0.1"})
    rag = RagAdapter(settings, retrieve_func=slow_retrieve)

    runtime = Runtime(
        settings=settings,
        rag=rag,
        knowledge_graph=None,  # type: ignore
        ml_models=None,  # type: ignore
    )
    runner = WorkflowRunner(runtime=runtime, nodes=_fake_nodes())
    service = OrchestrationService(runner=runner, settings=settings)

    request = AgentRequest(query="aturan", requested_intent="regulation", correlation_id=uuid4())
    response = service.handle(request)

    assert response.abstained is True
    traces = response.trace
    retrieval_trace = next(t for t in traces if t["node"] == "retrieval")
    assert retrieval_trace["status"] == "failed"
    assert "rag evidence is unavailable" in str(retrieval_trace["detail"]).lower()
