import sys
from uuid import uuid4

import pytest

from opticargo_agents.config import load_settings
from opticargo_agents.contracts import AgentRequest
from opticargo_agents.orchestrator.graph import WorkflowNodes, WorkflowRunner
from opticargo_agents.orchestrator.service import OrchestrationService
from opticargo_agents.runtime import Runtime


def shutdown_intent(query, requested_intent=None):
    # Simulate graceful shutdown signal (e.g. SIGTERM) handled as SystemExit
    sys.exit(0)


def test_shutdown_during_request_releases_semaphore() -> None:
    settings = load_settings({"AGENTS_MAX_CONCURRENT_REQUESTS": "1"})

    nodes = WorkflowNodes(intent=shutdown_intent)
    runtime = Runtime(
        settings=settings,
        rag=None,  # type: ignore
        knowledge_graph=None,  # type: ignore
        ml_models=None,  # type: ignore
    )
    runner = WorkflowRunner(runtime=runtime, nodes=nodes)
    service = OrchestrationService(runner=runner, settings=settings)

    request = AgentRequest(query="halo", correlation_id=uuid4())

    with pytest.raises(SystemExit):
        service.handle(request)

    # Verify semaphore was released
    dummy_nodes = WorkflowNodes(
        intent=lambda query, requested_intent=None: __import__("opticargo_agents.contracts", fromlist=["IntentResult"]).IntentResult(intent="unknown")
    )
    runner.nodes = dummy_nodes
    
    response = service.handle(request)
    assert response.intent == "unknown"
