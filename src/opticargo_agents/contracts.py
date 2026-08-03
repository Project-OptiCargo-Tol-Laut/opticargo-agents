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
    answer_available: bool = False
    citations: list[dict[str, Any]] = field(default_factory=list)
    requires_human_confirmation: bool = False
    abstained: bool = False
    abstention_reason: str | None = None
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)