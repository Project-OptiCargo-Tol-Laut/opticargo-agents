from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable
from uuid import NAMESPACE_URL, uuid5

from opticargo_agents.config import Settings
from opticargo_agents.contracts import (
    AgentRequest,
    GraphContextRequest,
    GraphContextResult,
    MLScoreResult,
    RetrievalRequest,
    SynthesisResult,
)
from opticargo_agents.errors import DependencyUnavailableError
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
            scoring_payload = build_cargo_scoring_payload(request, state.graph_context, self.runtime.settings)
            if scoring_payload is None:
                state.ml_score = MLScoreResult(
                    error=DependencyUnavailableError(
                        "No valid candidate data available for cargo scoring.",
                        dependency="ml_models",
                    ).envelope(),
                    fallback_used=True,
                    warnings=["Optimization skipped: no valid graph candidate to score."],
                )
            else:
                state.ml_score = self.nodes.optimization(
                    scoring_payload,
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
) -> dict[str, object] | None:
    if request.scoring_payload is not None:
        return request.scoring_payload
    shared_payload = build_shared_cargo_scoring_payload(request, graph_context, settings)
    if shared_payload is None:
        return None

    return _legacy_ml_payload_from_shared(shared_payload, settings)


def build_shared_cargo_scoring_payload(
    request: AgentRequest,
    graph_context: GraphContextResult | None,
    settings: Settings,
) -> dict[str, object] | None:
    """Build the canonical shared ML scoring contract from final KG context.

    The current `opticargo-ml-models` runtime still accepts its legacy strict
    payload.  Agents therefore builds this shared payload first, then transforms
    it to the legacy runtime shape before the HTTP call.
    """
    if graph_context is None or not graph_context.available or not graph_context.context:
        return None

    context = graph_context.context
    candidates = context.get("candidates") or []
    if not candidates:
        return None

    candidate = candidates[0]
    voyage_id = str(context.get("voyage_id") or request.voyage_id or uuid5(NAMESPACE_URL, str(request.correlation_id)))
    active_leg = context.get("active_leg") or {}
    ship_capacity = context.get("ship_capacity") or {}
    supplier = candidate.get("supplier") or {}
    origin_port = active_leg.get("origin_port") or {}
    destination_port = active_leg.get("destination_port") or {}
    candidate_origin_port = candidate.get("origin_port") or {}
    candidate_destination_port = candidate.get("destination_port") or {}
    route_id = str(active_leg.get("route_id") or uuid5(NAMESPACE_URL, f"{voyage_id}:route"))
    supplier_id = str(supplier.get("supplier_id") or uuid5(NAMESPACE_URL, f"{voyage_id}:supplier"))
    remaining_weight = _positive_float(
        ship_capacity.get("remaining_weight_ton"),
        candidate.get("available_weight_ton"),
        1.0,
    )
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
    supplier_rating = _rating_5_scale(supplier.get("rating"), settings.default_supplier_rating)
    distance_nm = _positive_float(active_leg.get("distance_nm"), 1.0)

    return {
        "correlation_id": str(request.correlation_id),
        "voyage": {
            "voyage_id": voyage_id,
            "remaining_weight_ton": remaining_weight,
            "remaining_volume_m3": remaining_volume,
        },
        "candidate": {
            "cargo_listing_id": str(candidate.get("cargo_listing_id") or uuid5(NAMESPACE_URL, f"{voyage_id}:candidate")),
            "cargo_weight_ton": candidate_weight,
            "cargo_volume_m3": candidate_volume,
            "features": {
                "commodity_id": _optional_id(candidate.get("commodity_id")),
                "origin_port_id": _optional_id(candidate_origin_port.get("port_id")),
                "destination_port_id": _optional_id(candidate_destination_port.get("port_id")),
                "supplier_verified": supplier.get("verified"),
                "graph_score": candidate.get("graph_score"),
                "capacity_compatible": bool(candidate.get("capacity_compatible", True)),
                "certification_compatible": bool(candidate.get("certification_compatible", True)),
                "supplier_rating_5_scale": supplier_rating,
            },
        },
        "route_schedule": {
            "distance_nm": distance_nm,
            "schedule_compatible": bool(candidate.get("schedule_compatible", True)),
            "route_features": {
                "route_id": route_id,
                "estimated_days": _optional_int(active_leg.get("estimated_days")),
                "route_type": active_leg.get("route_type"),
                "distance_km": max(distance_nm * 1.852, 1.0),
            },
        },
        "supplier_risk": {
            "supplier_id": supplier_id,
            "supplier_rating": supplier_rating,
            "risk_features": {
                "supplier_verified": supplier.get("verified"),
                "avg_monthly_volume_ton": _optional_positive_float(
                    supplier.get("avg_monthly_volume_ton")
                ),
                "distance_to_port_nm": _optional_non_negative_float(
                    supplier.get("distance_to_port_nm")
                ),
                "supplied_commodity_count": len(supplier.get("supplied_commodity_ids") or []),
            },
        },
    }


def _legacy_ml_payload_from_shared(
    shared_payload: dict[str, object],
    settings: Settings,
) -> dict[str, object]:
    voyage = dict(shared_payload["voyage"])  # type: ignore[arg-type]
    candidate = dict(shared_payload["candidate"])  # type: ignore[arg-type]
    route_schedule = dict(shared_payload["route_schedule"])  # type: ignore[arg-type]
    supplier_risk = dict(shared_payload["supplier_risk"])  # type: ignore[arg-type]
    route_features = dict(route_schedule.get("route_features") or {})
    risk_features = dict(supplier_risk.get("risk_features") or {})

    return {
        "trace_id": str(shared_payload["correlation_id"]),
        "voyage": {
            "voyage_id": voyage.get("voyage_id"),
            "route_id": route_features.get("route_id"),
            "route_distance_km": _positive_float(route_features.get("distance_km"), 1.0),
            "remaining_weight_ton": _positive_float(voyage.get("remaining_weight_ton"), 1.0),
            "remaining_volume_m3": _positive_float(voyage.get("remaining_volume_m3"), 1.0),
            "operating_cost_per_km_idr": settings.default_operating_cost_per_km_idr,
        },
        "candidate": {
            "cargo_listing_id": candidate.get("cargo_listing_id"),
            "supplier_id": supplier_risk.get("supplier_id"),
            "cargo_weight_ton": _positive_float(candidate.get("cargo_weight_ton"), 1.0),
            "cargo_volume_m3": _positive_float(candidate.get("cargo_volume_m3"), 1.0),
            "asking_price_per_ton_idr": settings.default_asking_price_per_ton_idr,
            "market_rate_per_ton_idr": settings.default_market_rate_per_ton_idr,
            "origin_distance_km": _non_negative_float(
                risk_features.get("distance_to_port_nm"),
                0.0,
            )
            * 1.852,
            "destination_distance_km": 0.0,
            "schedule_gap_hours": 0.0,
            "supplier_rating": _positive_float(
                supplier_risk.get("supplier_rating"),
                settings.default_supplier_rating,
            ),
            "supplier_success_rate": settings.default_supplier_success_rate,
            "supplier_cancellation_rate": settings.default_supplier_cancellation_rate,
            "commodity_compatibility": True,
            "certification_match": bool(
                dict(candidate.get("features") or {}).get("certification_compatible", True)
            ),
            "temperature_match": True,
            "weather_risk": 0.0,
            "port_congestion": 0.0,
            "historical_acceptance_rate": settings.default_supplier_success_rate,
        },
    }


def _optional_id(value: object) -> str | None:
    return str(value) if value else None


def _optional_int(value: object) -> int | None:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _optional_positive_float(value: object) -> float | None:
    try:
        parsed = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _optional_non_negative_float(value: object) -> float | None:
    try:
        parsed = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return parsed if parsed >= 0 else None


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


__all__ = [
    "WORKFLOW_ROUTES",
    "WorkflowNodes",
    "WorkflowRunner",
    "build_cargo_scoring_payload",
    "build_shared_cargo_scoring_payload",
]