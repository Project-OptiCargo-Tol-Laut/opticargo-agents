from opticargo_agents.contracts import AgentRequest, IntentResult, SynthesisResult
from opticargo_agents.orchestrator.graph import WorkflowNodes, WorkflowRunner
from opticargo_agents.orchestrator.service import OrchestrationService


def test_service_returns_response_from_workflow_state() -> None:
    nodes = WorkflowNodes(
        intent=lambda query, requested_intent=None: IntentResult(intent="unknown"),
    )
    service = OrchestrationService(runner=WorkflowRunner(nodes=nodes))

    response = service.handle(AgentRequest(query="halo"))

    assert response.intent == "unknown"
    assert response.route == ["intent", "synthesis"]
    assert response.abstained is True


def test_service_stream_emits_meta_and_done() -> None:
    nodes = WorkflowNodes(
        intent=lambda query, requested_intent=None: IntentResult(intent="unknown"),
    )
    service = OrchestrationService(runner=WorkflowRunner(nodes=nodes))

    events = list(service.stream(AgentRequest(query="halo")))

    assert events[0]["event"] == "meta"
    assert events[1]["event"] == "status"
    assert events[-1]["event"] == "done"


def test_service_stream_emits_safe_error() -> None:
    class BrokenRunner:
        def run(self, request):
            raise RuntimeError("boom")

    service = OrchestrationService(runner=BrokenRunner())

    events = list(service.stream(AgentRequest(query="halo")))

    assert events[0]["event"] == "meta"
    assert events[-1]["event"] == "error"
    assert events[-1]["message"] == "Agents request failed safely."
