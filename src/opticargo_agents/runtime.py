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
        knowledge_graph=_build_knowledge_graph_adapter(active_settings),
        ml_models=MLModelsClient(active_settings),
    )


def _build_knowledge_graph_adapter(settings: Settings) -> KnowledgeGraphAdapter:
    try:
        from opticargo_knowledge_graph.clients.neo4j import create_neo4j_driver
        from opticargo_knowledge_graph.config import GraphSettings
    except Exception:
        return KnowledgeGraphAdapter(settings)

    graph_settings = GraphSettings(
        neo4j_uri=settings.neo4j_uri,
        neo4j_user=settings.neo4j_user,
        neo4j_password=settings.neo4j_password,
        worker_heartbeat_seconds=30,
    )
    driver_cache: dict[str, object] = {}

    def session_factory():
        driver = driver_cache.get("driver")
        if driver is None:
            driver = create_neo4j_driver(graph_settings)
            driver_cache["driver"] = driver
        return driver.session(database=settings.neo4j_database)  # type: ignore[attr-defined]

    return KnowledgeGraphAdapter(settings, session_factory=session_factory)


__all__ = ["Runtime", "build_runtime"]
