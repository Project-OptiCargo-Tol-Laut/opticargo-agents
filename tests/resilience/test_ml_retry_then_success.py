import json
from uuid import uuid4

from opticargo_agents.clients.ml_models import MLModelsClient
from opticargo_agents.config import load_settings
from opticargo_agents.contracts import AgentRequest
from opticargo_agents.orchestrator.graph import WorkflowNodes, WorkflowRunner
from opticargo_agents.orchestrator.service import OrchestrationService
from opticargo_agents.runtime import Runtime


class FlakyTransport:
    def __init__(self):
        self.attempts = 0

    def post_json(self, url, payload, headers, timeout):
        self.attempts += 1
        if self.attempts == 1:
            raise TimeoutError("ML model timed out on first attempt")
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


def test_ml_retry_then_success_recovers_score() -> None:
    settings = load_settings(
        {
            "ML_MODELS_INTERNAL_URL": "http://fake-ml:8000",
            "ML_MODEL_MAX_RETRIES": "1",
        }
    )
    transport = FlakyTransport()
    client = MLModelsClient(settings, transport=transport)

    runtime = Runtime(
        settings=settings,
        rag=None,  # type: ignore
        knowledge_graph=None,  # type: ignore
        ml_models=client,
    )
    runner = WorkflowRunner(runtime=runtime, nodes=_fake_nodes())
    service = OrchestrationService(runner=runner, settings=settings)

    request = AgentRequest(query="matching", requested_intent="matching", voyage_id=uuid4())
    response = service.handle(request)

    assert transport.attempts == 2
    assert response.abstained is False

    traces = response.trace
    optimization_trace = next(t for t in traces if t["node"] == "optimization")
    assert optimization_trace["status"] == "completed"
    assert optimization_trace["detail"] is None
