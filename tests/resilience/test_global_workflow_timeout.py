import time
from uuid import uuid4

from opticargo_agents.api import _handle_internal_request
from opticargo_agents.config import load_settings
from opticargo_agents.contracts import AgentRequest
from opticargo_agents.orchestrator.graph import WorkflowNodes, WorkflowRunner
from opticargo_agents.orchestrator.service import OrchestrationService
from opticargo_agents.runtime import Runtime


def slow_intent(query, requested_intent=None):
    # Simulate a timeout exception bubbling up from a deep internal process
    # (e.g., if a global asyncio.wait_for or similar wrapper cancelled it,
    # or an unhandled timeout occurred)
    raise TimeoutError("Global timeout reached")


def test_global_workflow_timeout_handled_safely_by_api() -> None:
    settings = load_settings({})

    nodes = WorkflowNodes(intent=slow_intent)
    runtime = Runtime(
        settings=settings,
        rag=None,  # type: ignore
        knowledge_graph=None,  # type: ignore
        ml_models=None,  # type: ignore
    )
    runner = WorkflowRunner(runtime=runtime, nodes=nodes)
    service = OrchestrationService(runner=runner, settings=settings)

    payload = {"query": "halo", "correlation_id": str(uuid4())}
    response = _handle_internal_request(
        payload,
        internal_token=None,
        service=service,
        settings=settings,
    )

    assert response["ok"] is False
    assert response["error"]["code"] == "agents_internal_error"
    assert response["error"]["message"] == "Agents request failed safely."
