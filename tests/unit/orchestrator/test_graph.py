from uuid import uuid4

from opticargo_agents.contracts import (
    AgentRequest,
    GraphContextResult,
    IntentResult,
    MLScoreResult,
    RetrievalResult,
    SynthesisResult,
)
from opticargo_agents.config import load_settings
from opticargo_agents.orchestrator.graph import (
    WORKFLOW_ROUTES,
    WorkflowNodes,
    WorkflowRunner,
    build_cargo_scoring_payload,
    build_shared_cargo_scoring_payload,
)
from opticargo_shared.ml import CargoScoringRequest


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


def _graph_context() -> GraphContextResult:
    return GraphContextResult(
        context={
            "voyage_id": str(uuid4()),
            "active_leg": {
                "route_id": str(uuid4()),
                "route_type": "tol_laut",
                "distance_nm": "120",
                "estimated_days": 3,
                "origin_port": {"port_id": str(uuid4()), "name": "Sorong"},
                "destination_port": {"port_id": str(uuid4()), "name": "Makassar"},
            },
            "ship_capacity": {
                "total_weight_ton": "100",
                "used_weight_ton": "20",
                "remaining_weight_ton": "80",
                "remaining_volume_m3": "160",
            },
            "candidates": [
                {
                    "cargo_listing_id": str(uuid4()),
                    "commodity_id": str(uuid4()),
                    "available_weight_ton": "25",
                    "available_volume_m3": "40",
                    "certification_compatible": True,
                    "schedule_compatible": True,
                    "origin_port": {"port_id": str(uuid4()), "name": "Makassar"},
                    "destination_port": {"port_id": str(uuid4()), "name": "Sorong"},
                    "supplier": {
                        "supplier_id": str(uuid4()),
                        "rating": "0.8",
                        "verified": True,
                        "avg_monthly_volume_ton": "120",
                        "distance_to_port_nm": "10",
                        "supplied_commodity_ids": [str(uuid4())],
                    },
                }
            ],
        }
    )


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


def test_build_cargo_scoring_payload_uses_gateway_payload_first() -> None:
    payload = {"voyage": {"custom": True}, "candidate": {"custom": True}}
    request = AgentRequest(query="matching", scoring_payload=payload)

    assert build_cargo_scoring_payload(request, _graph_context(), load_settings({})) is payload


def test_build_cargo_scoring_payload_maps_graph_candidate_to_ml_contract_shape() -> None:
    request = AgentRequest(query="matching", voyage_id=uuid4())
    payload = build_cargo_scoring_payload(request, _graph_context(), load_settings({}))

    assert payload["trace_id"] == str(request.correlation_id)
    assert payload["voyage"]["route_distance_km"] > 1
    assert payload["voyage"]["remaining_weight_ton"] == 80.0
    assert payload["candidate"]["cargo_weight_ton"] == 25.0
    assert payload["candidate"]["cargo_volume_m3"] == 40.0
    assert payload["candidate"]["supplier_rating"] == 4.0
    assert payload["candidate"]["origin_distance_km"] == 18.52


def test_build_shared_cargo_scoring_payload_matches_shared_contract() -> None:
    request = AgentRequest(query="matching", voyage_id=uuid4())
    payload = build_shared_cargo_scoring_payload(request, _graph_context(), load_settings({}))

    assert payload is not None
    validated = CargoScoringRequest.model_validate(payload)
    assert str(validated.correlation_id) == str(request.correlation_id)
    assert validated.voyage.total_weight_ton == 100
    assert validated.voyage.used_weight_ton == 20
    assert validated.route_schedule.distance_nm == 120
    assert validated.route_schedule.estimated_days == 3
    assert validated.candidate.supplier_verified is True
    assert validated.supplier_risk.avg_monthly_volume_ton == 120


def test_runner_passes_graph_mapped_payload_to_optimization_node() -> None:
    seen = {}

    def optimization(payload, client, correlation_id=None):
        seen["payload"] = payload
        return MLScoreResult(score=0.8, hard_constraint_valid=True)

    nodes = WorkflowNodes(
        intent=lambda query, requested_intent=None: IntentResult(intent="matching", confidence=1),
        graph=lambda request, adapter: _graph_context(),
        retrieval=lambda request, adapter: RetrievalResult(
            query=request.query,
            citations=[{"title": "Dokumen A"}],
            confidence=0.8,
        ),
        optimization=optimization,
        synthesis=lambda retrieval=None, graph_context=None, ml_score=None: SynthesisResult(answer_available=True),
    )

    WorkflowRunner(nodes=nodes).run(AgentRequest(query="matching", voyage_id=uuid4()))

    assert seen["payload"]["candidate"]["cargo_weight_ton"] == 25.0


def test_runner_unknown_intent_asks_for_clarification() -> None:
    nodes = WorkflowNodes(intent=lambda query, requested_intent=None: IntentResult(intent="unknown"))
    state = WorkflowRunner(nodes=nodes).run(AgentRequest(query="halo"))

    assert state.route == ["intent", "synthesis"]
    assert state.synthesis.abstained is True
    assert "clarification" in state.synthesis.abstention_reason.lower()
