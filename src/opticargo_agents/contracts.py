from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
from uuid import UUID, uuid4

from opticargo_agents.errors import ErrorEnvelope


def payload_to_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return dict(value)
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if hasattr(value, "dict"):
        return value.dict()
    return {"value": value}


@dataclass(frozen=True)
class DependencyStatus:
    name: str
    status: str
    detail: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class IntentResult:
    intent: str
    confidence: float = 0.0
    source: str = "heuristic"
    rationale: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AgentRequest:
    query: str
    correlation_id: UUID = field(default_factory=uuid4)
    requested_intent: str | None = None
    voyage_id: UUID | None = None
    origin_port: str | None = None
    commodity: str | None = None
    top_k: int = 5
    min_score: float = 0.35
    scoring_payload: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def agent_request_from_payload(payload: dict[str, Any]) -> AgentRequest:
    query = str(payload.get("query") or payload.get("message") or "").strip()
    return AgentRequest(
        query=query,
        correlation_id=_uuid_or_new(payload.get("correlation_id")),
        requested_intent=_optional_str(payload.get("intent") or payload.get("requested_intent")),
        voyage_id=_optional_uuid(payload.get("voyage_id")),
        origin_port=_optional_str(payload.get("origin_port")),
        commodity=_optional_str(payload.get("commodity")),
        top_k=_positive_int(payload.get("top_k"), 5),
        min_score=_float_or_default(payload.get("min_score"), 0.35),
        scoring_payload=payload.get("scoring_payload") if isinstance(payload.get("scoring_payload"), dict) else None,
    )


@dataclass(frozen=True)
class NodeTrace:
    node: str
    status: str
    detail: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _optional_uuid(value: object) -> UUID | None:
    if value is None or value == "":
        return None
    try:
        return UUID(str(value))
    except (TypeError, ValueError):
        return None


def _uuid_or_new(value: object) -> UUID:
    return _optional_uuid(value) or uuid4()


def _positive_int(value: object, default: int) -> int:
    try:
        parsed = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def _float_or_default(value: object, default: float) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class RetrievalRequest:
    query: str
    correlation_id: UUID = field(default_factory=uuid4)
    top_k: int = 5
    min_score: float = 0.35
    graph_context: Any | None = None


@dataclass(frozen=True)
class RetrievalResult:
    query: str
    chunks: list[dict[str, Any]] = field(default_factory=list)
    citations: list[dict[str, Any]] = field(default_factory=list)
    confidence: float | None = None
    abstained: bool = False
    abstention_reason: str | None = None
    warnings: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)
    error: ErrorEnvelope | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["error"] = self.error.to_dict() if self.error else None
        return data


@dataclass(frozen=True)
class GraphContextRequest:
    correlation_id: UUID = field(default_factory=uuid4)
    voyage_id: UUID | None = None
    origin_port: str | None = None
    commodity: str | None = None
    limit: int = 20


@dataclass(frozen=True)
class GraphContextResult:
    context: dict[str, Any] | None = None
    warnings: list[str] = field(default_factory=list)
    error: ErrorEnvelope | None = None

    @property
    def available(self) -> bool:
        return self.context is not None and self.error is None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["error"] = self.error.to_dict() if self.error else None
        return data


@dataclass(frozen=True)
class MLScoreResult:
    score: float | None = None
    model_mode: str | None = None
    model_version: str | None = None
    fallback_used: bool = False
    hard_constraint_valid: bool | None = None
    feature_explanations: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)
    error: ErrorEnvelope | None = None

    @property
    def available(self) -> bool:
        return self.score is not None and self.error is None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["error"] = self.error.to_dict() if self.error else None
        return data


@dataclass(frozen=True)
class SynthesisResult:
    answer: str | None = None
    answer_available: bool = False
    citations: list[dict[str, Any]] = field(default_factory=list)
    requires_human_confirmation: bool = False
    abstained: bool = False
    abstention_reason: str | None = None
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
