import asyncio
import json

from opticargo_agents.api import (
    app,
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

    assert routes["chat"] == "/internal/v1/chat/stream"
    assert routes["recommendation"] == "/internal/v1/recommendations"
    assert routes["metrics"] == "/metrics"


def test_health_live_is_alive() -> None:
    assert health_live() == {"status": "alive"}


def test_asgi_app_serves_liveness_endpoint() -> None:
    messages = []

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        messages.append(message)

    scope = {"type": "http", "method": "GET", "path": "/health/live", "headers": []}
    asyncio.run(app(scope, receive, send))

    assert messages[0]["status"] == 200
    assert json.loads(messages[1]["body"]) == {"status": "alive"}


def test_asgi_app_serves_prometheus_metrics() -> None:
    messages = []

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        messages.append(message)

    asyncio.run(app({"type": "http", "method": "GET", "path": "/metrics", "headers": []}, receive, send))

    assert messages[0]["status"] == 200
    assert b"opticargo_agents_events_total" in messages[1]["body"]


def test_asgi_app_serves_chat_stream_with_sse_frames() -> None:
    messages = []
    body = json.dumps({"query": "halo", "intent": "unknown"}).encode()
    received = False

    async def receive():
        nonlocal received
        if received:
            return {"type": "http.disconnect"}
        received = True
        return {"type": "http.request", "body": body, "more_body": False}

    async def send(message):
        messages.append(message)

    asyncio.run(
        app(
            {"type": "http", "method": "POST", "path": "/internal/v1/chat/stream", "headers": []},
            receive,
            send,
        )
    )

    assert messages[0]["status"] == 200
    frames = b"".join(message.get("body", b"") for message in messages[1:])
    assert b"event: meta" in frames
    assert b"event: done" in frames


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


def test_recommendation_handler_cannot_override_matching_intent() -> None:
    captured = {}

    def intent(query, requested_intent=None):
        captured["requested_intent"] = requested_intent
        return IntentResult(intent="matching")

    service = OrchestrationService(
        runner=WorkflowRunner(nodes=WorkflowNodes(intent=intent)),
        settings=load_settings({}),
    )

    handle_internal_recommendation(
        {"message": "rekomendasikan", "intent": "regulation", "requested_intent": "route"},
        service=service,
        settings=load_settings({}),
    )

    assert captured["requested_intent"] == "matching"
