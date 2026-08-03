from opticargo_agents.api import (
    app_routes,
    handle_internal_chat,
    handle_internal_recommendation,
    health_live,
)
from opticargo_agents.config import load_settings
from opticargo_agents.contracts import IntentResult
from opticargo_agents.orchestrator.graph import WorkflowNodes, WorkflowRunner
from opticargo_agents.orchestrator.service import OrchestrationService


def _service() -> OrchestrationService:
    nodes = WorkflowNodes(intent=lambda query, requested_intent=None: IntentResult(intent="unknown"))
    return OrchestrationService(runner=WorkflowRunner(nodes=nodes), settings=load_settings({}))


def test_app_routes_expose_internal_contract_paths() -> None:
    routes = app_routes()

    assert routes["chat"] == "/internal/v1/chat"
    assert routes["recommendation"] == "/internal/v1/recommendations"


def test_health_live_is_alive() -> None:
    assert health_live() == {"status": "alive"}


def test_handle_internal_chat_returns_safe_response() -> None:
    response = handle_internal_chat({"message": "halo"}, service=_service(), settings=load_settings({}))

    assert response["ok"] is True
    assert response["data"]["intent"] == "unknown"
    assert response["error"] is None


def test_handle_internal_chat_returns_auth_error_when_token_invalid() -> None:
    settings = load_settings({"OPTICARGO_ENVIRONMENT": "production", "INTERNAL_SERVICE_TOKEN": "secret"})

    response = handle_internal_chat(
        {"message": "halo"},
        internal_token="wrong",
        service=_service(),
        settings=settings,
    )

    assert response["ok"] is False
    assert response["error"]["code"] == "unauthorized_internal_request"


def test_recommendation_handler_defaults_to_matching_intent() -> None:
    captured = {}

    def intent(query, requested_intent=None):
        captured["requested_intent"] = requested_intent
        return IntentResult(intent="unknown")

    service = OrchestrationService(
        runner=WorkflowRunner(nodes=WorkflowNodes(intent=intent)),
        settings=load_settings({}),
    )

    handle_internal_recommendation({"message": "rekomendasikan"}, service=service, settings=load_settings({}))

    assert captured["requested_intent"] == "matching"
