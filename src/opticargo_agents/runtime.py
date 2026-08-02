from __future__ import annotations

from dataclasses import dataclass

from opticargo_agents.clients import MLModelsClient
from opticargo_agents.config import Settings, get_settings
from opticargo_agents.integrations import KnowledgeGraphAdapter, RagAdapter


@dataclass(frozen=True)
class Runtime:
    settings: Settings
    rag: RagAdapter
    knowledge_graph: KnowledgeGraphAdapter
    ml_models: MLModelsClient


def build_runtime(settings: Settings | None = None) -> Runtime:
    active_settings = settings or get_settings()
    return Runtime(
        settings=active_settings,
        rag=RagAdapter(active_settings),
        knowledge_graph=KnowledgeGraphAdapter(active_settings),
        ml_models=MLModelsClient(active_settings),
    )


__all__ = ["Runtime", "build_runtime"]
