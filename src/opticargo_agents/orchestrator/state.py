from __future__ import annotations

from dataclasses import asdict, dataclass, field

from opticargo_agents.contracts import (
    AgentRequest,
    GraphContextResult,
    IntentResult,
    MLScoreResult,
    NodeTrace,
    RetrievalResult,
    SynthesisResult,
)


@dataclass
class WorkflowState:
    request: AgentRequest
    intent: IntentResult | None = None
    route: list[str] = field(default_factory=list)
    graph_context: GraphContextResult | None = None
    retrieval: RetrievalResult | None = None
    ml_score: MLScoreResult | None = None
    synthesis: SynthesisResult | None = None
    trace: list[NodeTrace] = field(default_factory=list)

    @property
    def final_intent(self) -> str:
        return self.intent.intent if self.intent is not None else "unknown"

    @property
    def done(self) -> bool:
        return self.synthesis is not None

    def add_trace(self, node: str, status: str, detail: str | None = None) -> None:
        self.trace.append(NodeTrace(node=node, status=status, detail=detail))

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def initial_state(request: AgentRequest) -> WorkflowState:
    return WorkflowState(request=request)


__all__ = ["WorkflowState", "initial_state"]
