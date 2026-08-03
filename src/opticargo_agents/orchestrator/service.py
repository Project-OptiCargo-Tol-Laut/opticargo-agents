from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
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
    answer_available: bool
    abstained: bool
    abstention_reason: str | None
    citations: list[dict[str, Any]]
    requires_human_confirmation: bool
    trace: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "correlation_id": self.correlation_id,
            "intent": self.intent,
            "route": self.route,
            "answer_available": self.answer_available,
            "abstained": self.abstained,
            "abstention_reason": self.abstention_reason,
            "citations": self.citations,
            "requires_human_confirmation": self.requires_human_confirmation,
            "trace": self.trace,
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
        yield {"event": "done", "correlation_id": response.correlation_id, "data": response.to_dict()}


def response_from_state(state: WorkflowState) -> OrchestrationResponse:
    synthesis = state.synthesis
    return OrchestrationResponse(
        correlation_id=str(state.request.correlation_id),
        intent=state.final_intent,
        route=list(state.route),
        answer_available=bool(synthesis and synthesis.answer_available),
        abstained=bool(synthesis and synthesis.abstained),
        abstention_reason=synthesis.abstention_reason if synthesis else "Workflow did not reach synthesis.",
        citations=list(synthesis.citations) if synthesis else [],
        requires_human_confirmation=bool(synthesis and synthesis.requires_human_confirmation),
        trace=[item.to_dict() for item in state.trace],
    )


__all__ = ["OrchestrationResponse", "OrchestrationService", "response_from_state"]
