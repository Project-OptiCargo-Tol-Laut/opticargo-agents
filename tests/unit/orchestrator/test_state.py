from opticargo_agents.contracts import AgentRequest
from opticargo_agents.orchestrator.state import initial_state


def test_initial_state_keeps_request_context() -> None:
    request = AgentRequest(query="aturan tol laut")
    state = initial_state(request)

    assert state.request is request
    assert state.final_intent == "unknown"
    assert state.done is False


def test_state_trace_records_node_status() -> None:
    state = initial_state(AgentRequest(query="aturan"))

    state.add_trace("intent", "completed", "regulation")

    assert state.trace[0].node == "intent"
    assert state.trace[0].status == "completed"
