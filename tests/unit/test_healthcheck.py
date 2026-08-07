from opticargo_agents import healthcheck
from opticargo_agents.health import HealthReport


def test_main_returns_zero_when_readiness_is_ready(monkeypatch) -> None:
    monkeypatch.setattr(
        healthcheck,
        "readiness_report",
        lambda: HealthReport(status="ready", dependencies=[]),
    )

    assert healthcheck.main() == 0


def test_main_returns_nonzero_when_readiness_is_degraded(monkeypatch) -> None:
    monkeypatch.setattr(
        healthcheck,
        "readiness_report",
        lambda: HealthReport(status="degraded", dependencies=[]),
    )

    assert healthcheck.main() == 1