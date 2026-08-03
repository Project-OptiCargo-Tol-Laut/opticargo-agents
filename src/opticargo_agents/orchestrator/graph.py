from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from opticargo_agents.contracts import (
    AgentRequest,
    GraphContextRequest,
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
                request.scoring_payload or _default_scoring_payload(request),
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


def _default_scoring_payload(request: AgentRequest) -> dict[str, object]:
    return {
        "trace_id": str(request.correlation_id),
        "voyage": {"voyage_id": str(request.voyage_id) if request.voyage_id else None},
        "candidate": {},
    }


def _clarification_message() -> str:
    return (
        "Saya belum bisa memastikan kebutuhan Anda. Pilih salah satu: regulation, "
        "matching, route, atau analytics."
    )


__all__ = ["WORKFLOW_ROUTES", "WorkflowNodes", "WorkflowRunner"]
