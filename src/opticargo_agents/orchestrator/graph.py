from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
from uuid import NAMESPACE_URL, uuid5

from opticargo_agents.config import Settings
from opticargo_agents.contracts import (
    AgentRequest,
    GraphContextRequest,
    GraphContextResult,
    RetrievalRequest,
    SynthesisResult,
)
from opticargo_agents.nodes import (
    run_cargo_scoring_node,
    run_graph_analysis_node,
    run_intent_node,
    run_retrieval_node,
    run_synthesis_node,
)
from opticargo_agents.orchestrator.state import WorkflowState, initial_state
from opticargo_agents.runtime import Runtime, build_runtime

RouteMap = dict[str, list[str]]

WORKFLOW_ROUTES: RouteMap = {
    "regulation": ["intent", "retrieval", "synthesis"],
    "matching": ["intent", "graph", "optimization", "retrieval", "synthesis"],
    "route": ["intent", "graph", "retrieval", "synthesis"],
    "analytics": ["intent", "graph", "synthesis"],
    "unknown": ["intent", "synthesis"],
}


@dataclass(frozen=True)
class WorkflowNodes:
    intent: Callable[..., object] = run_intent_node
    graph: Callable[..., object] = run_graph_analysis_node
    retrieval: Callable[..., object] = run_retrieval_node
    optimization: Callable[..., object] = run_cargo_scoring_node
    synthesis: Callable[..., object] = run_synthesis_node


class WorkflowRunner:
    def __init__(self, runtime: Runtime | None = None, nodes: WorkflowNodes | None = None) -> None:
        self.runtime = runtime or build_runtime()
        self.nodes = nodes or WorkflowNodes()

    def route_for(self, intent: str) -> list[str]:
        return list(WORKFLOW_ROUTES.get(intent, WORKFLOW_ROUTES["unknown"]))

    def run(self, request: AgentRequest) -> WorkflowState:
        state = initial_state(request)
        state.intent = self.nodes.intent(
            request.query,
            requested_intent=request.requested_intent,
        )
        state.add_trace("intent", "completed", state.intent.intent)
        state.route = self.route_for(state.intent.intent)

        if "graph" in state.route:
            state.graph_context = self.nodes.graph(
                GraphContextRequest(
                    correlation_id=request.correlation_id,
                    voyage_id=request.voyage_id,
                    origin_port=request.origin_port,
                    commodity=request.commodity,
                ),
                self.runtime.knowledge_graph,
            )
            state.add_trace(
                "graph",
                "completed" if state.graph_context.available else "failed",
                state.graph_context.error.code if state.graph_context.error else None,
            )

        if "optimization" in state.route:
            state.ml_score = self.nodes.optimization(
                build_cargo_scoring_payload(request, state.graph_context, self.runtime.settings),
                self.runtime.ml_models,
                correlation_id=str(request.correlation_id),
            )
            state.add_trace(
                "optimization",
                "completed" if state.ml_score.available else "fallback",
                state.ml_score.error.code if state.ml_score.error else None,
            )

        if "retrieval" in state.route:
            graph_context = state.graph_context.context if state.graph_context and state.graph_context.available else None
            state.retrieval = self.nodes.retrieval(
                RetrievalRequest(
                    query=request.query,
                    correlation_id=request.correlation_id,
                    top_k=request.top_k,
                    min_score=request.min_score,
                    graph_context=graph_context,
                ),
                self.runtime.rag,
            )
            state.add_trace(
                "retrieval",
                "completed" if not state.retrieval.abstained else "failed",
                state.retrieval.abstention_reason,
            )

        state.synthesis = self._synthesize(state)
        state.add_trace(
            "synthesis",
            "completed" if state.synthesis.answer_available else "failed",
            state.synthesis.abstention_reason,
        )
        return state

    def _synthesize(self, state: WorkflowState) -> SynthesisResult:
        if state.final_intent == "unknown":
            return SynthesisResult(
                answer=_clarification_message(),
                answer_available=False,
                abstained=True,
                abstention_reason="Intent is unknown; asking for clarification.",
            )
        return self.nodes.synthesis(
            retrieval=state.retrieval,
            graph_context=state.graph_context,
            ml_score=state.ml_score,
        )


def build_cargo_scoring_payload(
    request: AgentRequest,
    graph_context: GraphContextResult | None,
    settings: Settings,
) -> dict[str, object]:
    if request.scoring_payload is not None:
        return request.scoring_payload
    if graph_context is None or not graph_context.available or not graph_context.context:
        return _default_scoring_payload(request)

    context = graph_context.context
    candidates = context.get("candidates") or []
    if not candidates:
        return _default_scoring_payload(request)

    candidate = candidates[0]
    voyage_id = str(context.get("voyage_id") or request.voyage_id or uuid5(NAMESPACE_URL, str(request.correlation_id)))
    active_leg = context.get("active_leg") or {}
    ship_capacity = context.get("ship_capacity") or {}
    supplier = candidate.get("supplier") or {}
    remaining_weight = _positive_float(ship_capacity.get("remaining_weight_ton"), candidate.get("available_weight_ton"), 1.0)
    candidate_weight = min(
        _positive_float(candidate.get("available_weight_ton"), 1.0),
        remaining_weight,
    )
    candidate_volume = _positive_float(
        candidate.get("available_volume_m3"),
        candidate_weight * settings.default_cargo_volume_m3_per_ton,
    )
    remaining_volume = _positive_float(
        ship_capacity.get("remaining_volume_m3"),
        max(candidate_volume, remaining_weight * settings.default_cargo_volume_m3_per_ton),
    )
    distance_nm = _positive_float(active_leg.get("distance_nm"), 1.0)
    route_distance_km = max(distance_nm * 1.852, 1.0)
    supplier_rating = _rating_5_scale(supplier.get("rating"), settings.default_supplier_rating)

    return {
        "trace_id": str(request.correlation_id),
        "voyage": {
            "voyage_id": voyage_id,
            "route_id": str(active_leg.get("route_id") or uuid5(NAMESPACE_URL, f"{voyage_id}:route")),
            "route_distance_km": route_distance_km,
            "remaining_weight_ton": remaining_weight,
            "remaining_volume_m3": remaining_volume,
            "operating_cost_per_km_idr": settings.default_operating_cost_per_km_idr,
        },
        "candidate": {
            "cargo_listing_id": str(candidate.get("cargo_listing_id") or uuid5(NAMESPACE_URL, f"{voyage_id}:candidate")),
            "supplier_id": str(supplier.get("supplier_id") or uuid5(NAMESPACE_URL, f"{voyage_id}:supplier")),
            "cargo_weight_ton": candidate_weight,
            "cargo_volume_m3": candidate_volume,
            "asking_price_per_ton_idr": settings.default_asking_price_per_ton_idr,
            "market_rate_per_ton_idr": settings.default_market_rate_per_ton_idr,
            "origin_distance_km": _non_negative_float(supplier.get("distance_to_port_nm"), 0.0) * 1.852,
            "destination_distance_km": 0.0,
            "schedule_gap_hours": 0.0,
            "supplier_rating": supplier_rating,
            "supplier_success_rate": settings.default_supplier_success_rate,
            "supplier_cancellation_rate": settings.default_supplier_cancellation_rate,
            "commodity_compatibility": True,
            "certification_match": bool(candidate.get("certification_compatible", True)),
            "temperature_match": True,
            "weather_risk": 0.0,
            "port_congestion": 0.0,
            "historical_acceptance_rate": settings.default_supplier_success_rate,
        },
    }


def _default_scoring_payload(request: AgentRequest) -> dict[str, object]:
    return {
        "trace_id": str(request.correlation_id),
        "voyage": {"voyage_id": str(request.voyage_id) if request.voyage_id else None},
        "candidate": {},
    }


def _positive_float(*values: object) -> float:
    for value in values:
        try:
            parsed = float(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            continue
        if parsed > 0:
            return parsed
    return 1.0


def _non_negative_float(value: object, default: float) -> float:
    try:
        parsed = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default
    return parsed if parsed >= 0 else default


def _rating_5_scale(value: object, default: float) -> float:
    rating = _positive_float(value, default)
    if rating <= 1:
        rating *= 5
    return min(max(rating, 1.0), 5.0)


def _clarification_message() -> str:
    return (
        "Saya belum bisa memastikan kebutuhan Anda. Pilih salah satu: regulation, "
        "matching, route, atau analytics."
    )


__all__ = ["WORKFLOW_ROUTES", "WorkflowNodes", "WorkflowRunner", "build_cargo_scoring_payload"]
