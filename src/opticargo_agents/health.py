from __future__ import annotations

from dataclasses import asdict, dataclass, field

from opticargo_agents.clients import MLModelsClient
from opticargo_agents.config import Settings, get_settings
from opticargo_agents.integrations import KnowledgeGraphAdapter, RagAdapter


@dataclass(frozen=True)
class HealthReport:
    status: str
    dependencies: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def readiness_report(
    settings: Settings | None = None,
    rag: RagAdapter | None = None,
    knowledge_graph: KnowledgeGraphAdapter | None = None,
    ml_models: MLModelsClient | None = None,
) -> HealthReport:
    active_settings = settings or get_settings()
    runtime = None
    if rag is None or knowledge_graph is None or ml_models is None:
        from opticargo_agents.runtime import build_runtime

        runtime = build_runtime(active_settings)
    dependencies = [
        (rag or runtime.rag).health(),  # type: ignore[union-attr]
        (knowledge_graph or runtime.knowledge_graph).health(),  # type: ignore[union-attr]
        (ml_models or runtime.ml_models).health(),  # type: ignore[union-attr]
    ]
    required = {
        "rag": active_settings.readiness_require_qdrant,
        "knowledge_graph": active_settings.readiness_require_neo4j,
        "ml_models": active_settings.readiness_require_ml_models,
    }
    degraded_required = [
        item for item in dependencies if required.get(item["name"], False) and item["status"] != "ready"
    ]
    return HealthReport(status="degraded" if degraded_required else "ready", dependencies=dependencies)


def liveness_report() -> dict[str, str]:
    return {"status": "alive"}


__all__ = ["HealthReport", "liveness_report", "readiness_report"]
