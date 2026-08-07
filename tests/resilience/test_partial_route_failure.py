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
    from opticargo_agents.contracts import GraphContextResult, IntentResult, MLScoreResult
    from opticargo_agents.nodes import run_retrieval_node, run_synthesis_node

    return WorkflowNodes(
        intent=lambda query, requested_intent=None: IntentResult(intent="matching", confidence=1),
        graph=lambda request, adapter: GraphContextResult(
            context={"candidates": [{"cargo_listing_id": "c1", "available_weight_ton": 10}]}
        ),
        retrieval=run_retrieval_node,
        optimization=lambda payload, client, correlation_id=None: MLScoreResult(score=0.9, hard_constraint_valid=True),
        synthesis=run_synthesis_node,
    )


def test_partial_route_failure_preserves_overall_workflow() -> None:
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

    request = AgentRequest(query="matching", requested_intent="matching", correlation_id=uuid4(), voyage_id=uuid4())
    response = service.handle(request)

    # RAG failed, but the intent was 'matching' which does not strictly require RAG 
    # to provide an answer (it uses RAG optionally, or might abstain if it was regulation).
    # The synthesis node for 'matching' will succeed even if RAG abstained.
    assert response.abstained is False
    assert response.answer_available is True
    assert response.requires_human_confirmation is True

    traces = response.trace
    
    # Graph and Optimization succeeded
    assert next(t for t in traces if t["node"] == "graph")["status"] == "completed"
    assert next(t for t in traces if t["node"] == "optimization")["status"] == "completed"
    
    # Retrieval failed
    retrieval_trace = next(t for t in traces if t["node"] == "retrieval")
    assert retrieval_trace["status"] == "failed"
    
    # Synthesis succeeded
    assert next(t for t in traces if t["node"] == "synthesis")["status"] == "completed"
