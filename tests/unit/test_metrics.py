from opticargo_agents.metrics import InMemoryMetrics


def test_in_memory_metrics_counts_events() -> None:
    metrics = InMemoryMetrics()

    metrics.inc("node.retrieve.completed")
    metrics.inc("node.retrieve.completed", 2)

    assert metrics.snapshot()["node.retrieve.completed"] == 3
