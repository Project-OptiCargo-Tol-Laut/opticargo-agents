from uuid import uuid4

from opticargo_agents.clients.ml_models import MLModelsClient
from opticargo_agents.config import load_settings
from opticargo_agents.contracts import AgentRequest
from opticargo_agents.orchestrator.graph import WorkflowNodes, WorkflowRunner
from opticargo_agents.orchestrator.service import OrchestrationService
from opticargo_agents.runtime import Runtime


class RestartingTransport:
    def __init__(self):
        self.calls = 0

    def post_json(self, url, payload, headers, timeout):
        self.calls += 1
        if self.calls == 1:
            from urllib.error import URLError
            raise URLError("Connection refused")
        return {
            "score": 0.85,
            "model_mode": "trained",
            "model_version": "v2",
            "hard_constraint_valid": True,
            "fallback_used": False,
        }


def _fake_nodes() -> WorkflowNodes:
    from opticargo_agents.contracts import GraphContextResult, IntentResult, RetrievalResult
    from opticargo_agents.nodes import run_cargo_scoring_node, run_synthesis_node

    return WorkflowNodes(
        intent=lambda query, requested_intent=None: IntentResult(intent="matching", confidence=1),
        graph=lambda request, adapter: GraphContextResult(
            context={"candidates": [{"cargo_listing_id": "c1", "available_weight_ton": 10}]}
        ),
        retrieval=lambda request, adapter: RetrievalResult(
            query=request.query, citations=[{"title": "Doc"}], confidence=0.8
        ),
        optimization=run_cargo_scoring_node,
        synthesis=run_synthesis_node,
    )


def test_dependency_restart_recovery() -> None:
    settings = load_settings({
        "ML_MODELS_INTERNAL_URL": "http://fake-ml:8000",
        "ML_MODEL_MAX_RETRIES": "0"
    })
    transport = RestartingTransport()
    client = MLModelsClient(settings, transport=transport)

    runtime = Runtime(
        settings=settings,
        rag=None,  # type: ignore
        knowledge_graph=None,  # type: ignore
        ml_models=client,
    )
    runner = WorkflowRunner(runtime=runtime, nodes=_fake_nodes())
    service = OrchestrationService(runner=runner, settings=settings)

    # First request: dependency is down
    request1 = AgentRequest(query="matching", requested_intent="matching", correlation_id=uuid4(), voyage_id=uuid4())
    response1 = service.handle(request1)
    
    # Verify fallback used
    opt_trace1 = next(t for t in response1.trace if t["node"] == "optimization")
    assert opt_trace1["status"] == "fallback"

    # Second request: dependency is back up
    request2 = AgentRequest(query="matching", requested_intent="matching", correlation_id=uuid4(), voyage_id=uuid4())
    response2 = service.handle(request2)

    # Verify recovery successful
    opt_trace2 = next(t for t in response2.trace if t["node"] == "optimization")
    assert opt_trace2["status"] == "completed"
    assert opt_trace2["detail"] is None
