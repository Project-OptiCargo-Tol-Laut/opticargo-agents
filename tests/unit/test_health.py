from opticargo_agents.config import load_settings
from opticargo_agents.health import liveness_report, readiness_report


class ReadyDependency:
    def __init__(self, name: str) -> None:
        self.name = name

    def health(self):
        return {"name": self.name, "status": "ready", "detail": "test"}


class DegradedDependency:
    def __init__(self, name: str) -> None:
        self.name = name

    def health(self):
        return {"name": self.name, "status": "degraded", "detail": "test"}


def test_liveness_report_is_alive() -> None:
    assert liveness_report() == {"status": "alive"}


def test_readiness_respects_required_dependencies() -> None:
    settings = load_settings({"READINESS_REQUIRE_ML_MODELS": "true"})

    report = readiness_report(
        settings,
        rag=ReadyDependency("rag"),
        knowledge_graph=ReadyDependency("knowledge_graph"),
        ml_models=DegradedDependency("ml_models"),
    )

    assert report.status == "degraded"
