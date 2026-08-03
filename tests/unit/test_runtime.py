from opticargo_agents.config import Settings
from opticargo_agents.runtime import build_runtime


def test_build_runtime_configures_knowledge_graph_adapter() -> None:
    runtime = build_runtime(Settings(neo4j_password="password"))

    assert runtime.knowledge_graph.health()["name"] == "knowledge_graph"
