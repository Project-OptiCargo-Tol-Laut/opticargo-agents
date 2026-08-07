import time
from threading import Thread
from uuid import uuid4
import pytest

from opticargo_agents.config import load_settings
from opticargo_agents.contracts import AgentRequest
from opticargo_agents.orchestrator.graph import WorkflowNodes, WorkflowRunner
from opticargo_agents.orchestrator.service import OrchestrationService
from opticargo_agents.runtime import Runtime


def test_bounded_concurrency_rejects_excessive_requests() -> None:
    # Max concurrency 1, request timeout 0.1s
    settings = load_settings({
        "AGENTS_MAX_CONCURRENT_REQUESTS": "1",
        "AGENTS_REQUEST_TIMEOUT_SECONDS": "0.1"
    })

    def slow_intent(query, requested_intent=None):
        time.sleep(0.3)
        from opticargo_agents.contracts import IntentResult
        return IntentResult(intent="unknown")

    nodes = WorkflowNodes(intent=slow_intent)
    runtime = Runtime(
        settings=settings,
        rag=None,  # type: ignore
        knowledge_graph=None,  # type: ignore
        ml_models=None,  # type: ignore
    )
    runner = WorkflowRunner(runtime=runtime, nodes=nodes)
    service = OrchestrationService(runner=runner, settings=settings)

    errors = []

    def worker():
        try:
            req = AgentRequest(query="halo", correlation_id=uuid4())
            service.handle(req)
        except Exception as e:
            errors.append(e)

    # Thread 1 starts and sleeps in intent node
    t1 = Thread(target=worker)
    t1.start()
    
    # Wait for t1 to acquire semaphore
    time.sleep(0.05)
    
    # Thread 2 starts, will block on semaphore and timeout after 0.1s
    t2 = Thread(target=worker)
    t2.start()

    t1.join()
    t2.join()

    # One of the threads should have successfully finished, the other got TimeoutError
    assert len(errors) == 1
    assert isinstance(errors[0], TimeoutError)
    assert "concurrency limit was reached" in str(errors[0]).lower()
