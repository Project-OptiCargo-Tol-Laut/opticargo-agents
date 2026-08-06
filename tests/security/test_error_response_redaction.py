"""Security layer: pastikan response error tidak pernah membocorkan
credential, token, atau detail exception mentah (raw provider body).

Rujukan: docs/SECURITY_BOUNDARY.md, docs/GUARDRAILS_AND_HUMAN_CONFIRMATION.md
"""

import json

from opticargo_agents.api import handle_internal_chat
from opticargo_agents.config import load_settings
from opticargo_agents.contracts import IntentResult
from opticargo_agents.errors import DependencyUnavailableError
from opticargo_agents.orchestrator.graph import WorkflowNodes, WorkflowRunner
from opticargo_agents.orchestrator.service import OrchestrationService


def _service_with_failing_intent(exc: Exception) -> OrchestrationService:
    def intent(query, requested_intent=None):
        raise exc

    nodes = WorkflowNodes(intent=intent)
    return OrchestrationService(runner=WorkflowRunner(nodes=nodes), settings=load_settings({}))


def test_error_response_never_includes_caller_supplied_token() -> None:
    secret_token = "caller-supplied-secret-xyz"
    service = _service_with_failing_intent(
        DependencyUnavailableError("Neo4j connection refused.", dependency="knowledge_graph")
    )

    response = handle_internal_chat(
        {"message": "halo"},
        internal_token=secret_token,
        service=service,
        settings=load_settings({}),
    )

    serialized = json.dumps(response)
    assert secret_token not in serialized


def test_unauthorized_response_does_not_leak_configured_secret() -> None:
    settings = load_settings({"OPTICARGO_ENVIRONMENT": "production", "INTERNAL_SERVICE_TOKEN": "real-secret-abc"})

    response = handle_internal_chat(
        {"message": "halo"},
        internal_token="wrong-guess",
        service=_service_with_failing_intent(RuntimeError("unused")),
        settings=settings,
    )

    serialized = json.dumps(response)
    assert response["error"]["code"] == "unauthorized_internal_request"
    assert "real-secret-abc" not in serialized
    assert "wrong-guess" not in serialized


def test_generic_exception_never_leaks_raw_exception_message() -> None:
    sensitive_detail = "password=hunter2;connection_string=postgresql://user:hunter2@db"
    service = _service_with_failing_intent(RuntimeError(sensitive_detail))

    response = handle_internal_chat(
        {"message": "halo"},
        service=service,
        settings=load_settings({}),
    )

    serialized = json.dumps(response)
    assert response["ok"] is False
    assert response["error"]["code"] == "agents_internal_error"
    assert sensitive_detail not in serialized
    assert "hunter2" not in serialized


def test_dependency_error_message_is_surfaced_but_without_secret() -> None:
    """AgentsError message boleh muncul (untuk observability), TAPI tidak boleh
    mengandung token/secret -- ini dijamin karena adapter tidak pernah
    menyisipkan token ke pesan error, bukan karena pesannya disembunyikan."""
    service = _service_with_failing_intent(
        DependencyUnavailableError("Neo4j connection refused.", dependency="knowledge_graph")
    )

    response = handle_internal_chat(
        {"message": "halo"},
        internal_token="some-caller-token",
        service=service,
        settings=load_settings({}),
    )

    assert response["ok"] is False
    assert response["error"]["dependency"] == "knowledge_graph"
    assert "some-caller-token" not in json.dumps(response)