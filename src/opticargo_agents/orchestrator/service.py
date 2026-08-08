from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from threading import BoundedSemaphore
from typing import Any

from opticargo_agents.config import Settings, get_settings
from opticargo_agents.contracts import AgentRequest
from opticargo_agents.orchestrator.graph import WorkflowRunner
from opticargo_agents.orchestrator.state import WorkflowState


@dataclass(frozen=True)
class OrchestrationResponse:
    correlation_id: str
    intent: str
    route: list[str]
    answer: str | None
    answer_available: bool
    abstained: bool
    abstention_reason: str | None
    citations: list[dict[str, Any]]
    requires_human_confirmation: bool
    trace: list[dict[str, Any]]
    recommendations: list[dict[str, Any]] = field(default_factory=list)
    aggregate_confidence: float | None = None
    fallback_used: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "correlation_id": self.correlation_id,
            "intent": self.intent,
            "route": self.route,
            "answer": self.answer,
            "answer_available": self.answer_available,
            "abstained": self.abstained,
            "abstention_reason": self.abstention_reason,
            "citations": self.citations,
            "requires_human_confirmation": self.requires_human_confirmation,
            "trace": self.trace,
            "recommendations": self.recommendations,
            "aggregate_confidence": self.aggregate_confidence,
            "fallback_used": self.fallback_used,
        }


class OrchestrationService:
    def __init__(self, runner: WorkflowRunner | None = None, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.runner = runner or WorkflowRunner()
        self._semaphore = BoundedSemaphore(max(1, self.settings.max_concurrent_requests))

    def handle(self, request: AgentRequest) -> OrchestrationResponse:
        acquired = self._semaphore.acquire(timeout=self.settings.request_timeout_seconds)
        if not acquired:
            raise TimeoutError("Agents concurrency limit was reached.")
        try:
            state = self.runner.run(request)
            return response_from_state(state)
        finally:
            self._semaphore.release()

    def stream(self, request: AgentRequest) -> Iterator[dict[str, Any]]:
        yield {
            "event": "meta",
            "correlation_id": str(request.correlation_id),
        }
        yield {
            "event": "status",
            "correlation_id": str(request.correlation_id),
            "data": {"status": "running"},
        }
        try:
            response = self.handle(request)
        except Exception as exc:
            yield {
                "event": "error",
                "correlation_id": str(request.correlation_id),
                "code": exc.__class__.__name__,
                "message": "Agents request failed safely.",
            }
            return
        for citation in response.citations:
            yield {"event": "citation", "correlation_id": response.correlation_id, "data": citation}
        if response.answer_available and response.answer:
            # Keep chunks bounded and UTF-8 safe; the Gateway may forward these
            # events directly to the browser as SSE.
            for offset in range(0, len(response.answer), 512):
                yield {
                    "event": "token",
                    "correlation_id": response.correlation_id,
                    "data": {"text": response.answer[offset : offset + 512]},
                }
        yield {"event": "done", "correlation_id": response.correlation_id, "data": response.to_dict()}


def response_from_state(state: WorkflowState) -> OrchestrationResponse:
    synthesis = state.synthesis
    return OrchestrationResponse(
        correlation_id=str(state.request.correlation_id),
        intent=state.final_intent,
        route=list(state.route),
        answer=synthesis.answer if synthesis else None,
        answer_available=bool(synthesis and synthesis.answer_available),
        abstained=bool(synthesis and synthesis.abstained),
        abstention_reason=synthesis.abstention_reason if synthesis else "Workflow did not reach synthesis.",
        citations=list(synthesis.citations) if synthesis else [],
        requires_human_confirmation=bool(synthesis and synthesis.requires_human_confirmation),
        trace=[item.to_dict() for item in state.trace],
        recommendations=_recommendations_from_state(state),
        aggregate_confidence=state.ml_score.score if state.ml_score else None,
        fallback_used=bool(state.ml_score and state.ml_score.fallback_used),
    )


def _recommendations_from_state(state: WorkflowState) -> list[dict[str, Any]]:
    """Expose a bounded, Gateway-safe ranking without leaking raw KG records."""
    if state.final_intent != "matching" or not state.graph_context or not state.graph_context.context:
        return []
    if state.ml_score and state.ml_score.error and state.ml_score.error.code == "hard_constraint_violation":
        # A candidate rejected by a hard constraint must never be exposed as a
        # ranked recommendation, even if graph context still contains it.
        return []
    candidates = state.graph_context.context.get("candidates") or []
    score = state.ml_score.score if state.ml_score else None
    return [
        {
            "rank": index,
            "cargo_listing_id": candidate.get("cargo_listing_id"),
            "commodity_name": candidate.get("commodity_name"),
            "available_weight_ton": candidate.get("available_weight_ton"),
            "supplier": candidate.get("supplier"),
            "score": score if index == 1 else candidate.get("graph_score"),
            "hard_constraint_valid": state.ml_score.hard_constraint_valid
            if index == 1 and state.ml_score
            else candidate.get("capacity_compatible", True),
            "model_mode": state.ml_score.model_mode if index == 1 and state.ml_score else None,
            "feature_explanations": state.ml_score.feature_explanations
            if index == 1 and state.ml_score
            else [],
            "requires_human_confirmation": True,
        }
        for index, candidate in enumerate(candidates[:10], start=1)
        if isinstance(candidate, dict)
    ]


__all__ = ["OrchestrationResponse", "OrchestrationService", "response_from_state"]
