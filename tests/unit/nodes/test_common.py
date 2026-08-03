from opticargo_agents.nodes.common import timed_node


def test_timed_node_returns_result_and_trace() -> None:
    result, trace = timed_node("sample", lambda: "ok")

    assert result == "ok"
    assert trace.node == "sample"
    assert trace.status == "completed"
