from uuid import uuid4

from opticargo_agents.contracts import (
    AgentRequest,
    GraphContextResult,
    IntentResult,
    MLScoreResult,
    RetrievalResult,
    SynthesisResult,
)
from opticargo_agents.orchestrator.graph import WORKFLOW_ROUTES, WorkflowNodes, WorkflowRunner


def _runner() -> WorkflowRunner:
    nodes = WorkflowNodes(
        intent=lambda query, requested_intent=None: IntentResult(intent=requested_intent or "regulation", confidence=1),
        graph=lambda request, adapter: GraphContextResult(context={"candidates": [{"id": "c1"}]}),
        retrieval=lambda request, adapter: RetrievalResult(
            query=request.query,
            citations=[{"title": "Dokumen A"}],
            confidence=0.8,
        ),
        optimization=lambda payload, client, correlation_id=None: MLScoreResult(
            score=0.8,
            hard_constraint_valid=True,
        ),
        synthesis=lambda retrieval=None, graph_context=None, ml_score=None: SynthesisResult(
            answer_available=True,
            citations=list(retrieval.citations) if retrieval else [],
            requires_human_confirmation=ml_score is not None,
        ),
    )
    return WorkflowRunner(nodes=nodes)


def test_route_map_matches_documented_workflow() -> None:
    assert WORKFLOW_ROUTES["regulation"] == ["intent", "retrieval", "synthesis"]
    assert WORKFLOW_ROUTES["matching"] == ["intent", "graph", "optimization", "retrieval", "synthesis"]
    assert WORKFLOW_ROUTES["unknown"] == ["intent", "synthesis"]


def test_runner_executes_regulation_route() -> None:
    state = _runner().run(AgentRequest(query="aturan dokumen", requested_intent="regulation"))

    assert state.final_intent == "regulation"
    assert state.route == ["intent", "retrieval", "synthesis"]
    assert state.graph_context is None
    assert state.ml_score is None
    assert state.retrieval is not None
    assert state.synthesis.answer_available is True


def test_runner_executes_matching_route() -> None:
    state = _runner().run(
        AgentRequest(query="matching muatan", requested_intent="matching", voyage_id=uuid4())
    )

    assert state.route == ["intent", "graph", "optimization", "retrieval", "synthesis"]
    assert state.graph_context.available is True
    assert state.ml_score.available is True
    assert state.synthesis.requires_human_confirmation is True


def test_runner_unknown_intent_asks_for_clarification() -> None:
    nodes = WorkflowNodes(intent=lambda query, requested_intent=None: IntentResult(intent="unknown"))
    state = WorkflowRunner(nodes=nodes).run(AgentRequest(query="halo"))

    assert state.route == ["intent", "synthesis"]
    assert state.synthesis.abstained is True
    assert "clarification" in state.synthesis.abstention_reason.lower()
