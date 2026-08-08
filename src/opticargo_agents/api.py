from __future__ import annotations

import json
from typing import Any

from opticargo_agents.config import Settings, get_settings
from opticargo_agents.contracts import agent_request_from_payload
from opticargo_agents.errors import AgentsError
from opticargo_agents.health import liveness_report, readiness_report
from opticargo_agents.metrics import prometheus_text
from opticargo_agents.orchestrator import OrchestrationService
from opticargo_agents.security import validate_internal_token


def app_routes() -> dict[str, str]:
    return {
        "liveness": "/health/live",
        "readiness": "/health/ready",
        "recommendation": "/internal/v1/recommendations",
        "chat": "/internal/v1/chat/stream",
        "metrics": "/metrics",
    }


def health_live() -> dict[str, str]:
    return liveness_report()


def health_ready() -> dict[str, object]:
    return readiness_report().to_dict()


def handle_internal_chat(
    payload: dict[str, Any],
    *,
    internal_token: str | None = None,
    service: OrchestrationService | None = None,
    settings: Settings | None = None,
) -> dict[str, Any]:
    return _handle_internal_request(payload, internal_token=internal_token, service=service, settings=settings)


def handle_internal_recommendation(
    payload: dict[str, Any],
    *,
    internal_token: str | None = None,
    service: OrchestrationService | None = None,
    settings: Settings | None = None,
) -> dict[str, Any]:
    # Recommendation is an explicit matching-only boundary; caller fields
    # must not be able to route this endpoint into regulation/route/analytics.
    enriched_payload = {**payload, "requested_intent": "matching", "intent": "matching"}
    return _handle_internal_request(
        enriched_payload,
        internal_token=internal_token,
        service=service,
        settings=settings,
    )


def _handle_internal_request(
    payload: dict[str, Any],
    *,
    internal_token: str | None,
    service: OrchestrationService | None,
    settings: Settings | None,
) -> dict[str, Any]:
    active_settings = settings or get_settings()
    try:
        validate_internal_token(internal_token, active_settings)
        request = agent_request_from_payload(payload)
        response = (service or OrchestrationService(settings=active_settings)).handle(request)
        return {"ok": True, "data": response.to_dict(), "error": None}
    except AgentsError as exc:
        return {"ok": False, "data": None, "error": exc.envelope().to_dict()}
    except Exception:
        return {
            "ok": False,
            "data": None,
            "error": {
                "code": "agents_internal_error",
                "message": "Agents request failed safely.",
                "dependency": None,
                "retryable": False,
            },
        }


async def app(scope: dict[str, Any], receive: Any, send: Any) -> None:
    """Small ASGI app used by the infra `uvicorn opticargo_agents.api:app` command.

    The main business handlers remain plain functions so unit tests and Gateway
    integration can call them directly.  This ASGI wrapper provides the runtime
    health and internal JSON endpoints required by Docker Compose.
    """
    if scope.get("type") != "http":
        await _send_json(send, 404, {"error": "unsupported_scope"})
        return

    method = str(scope.get("method", "GET")).upper()
    path = str(scope.get("path", "/"))
    headers = _headers(scope)

    if method == "GET" and path == "/health/live":
        await _send_json(send, 200, health_live())
        return
    if method == "GET" and path == "/health/ready":
        payload = health_ready()
        status_code = 200 if payload.get("status") == "ready" else 503
        await _send_json(send, status_code, payload)
        return
    if method == "GET" and path == "/routes":
        await _send_json(send, 200, app_routes())
        return
    if method == "GET" and path == "/metrics":
        await _send_text(send, 200, "text/plain; version=0.0.4; charset=utf-8", prometheus_text())
        return

    if method == "POST" and path == "/internal/v1/chat/stream":
        payload = await _read_json(receive)
        if headers.get("x-correlation-id") and not payload.get("correlation_id"):
            payload["correlation_id"] = headers["x-correlation-id"]
        await _send_sse(send, payload, internal_token=headers.get("x-internal-service-token"))
        return

    if method == "POST" and path in {"/internal/v1/chat", "/internal/v1/recommendations"}:
        payload = await _read_json(receive)
        if headers.get("x-correlation-id") and not payload.get("correlation_id"):
            payload["correlation_id"] = headers["x-correlation-id"]
        token = headers.get("x-internal-service-token")
        if path.endswith("/chat"):
            result = handle_internal_chat(payload, internal_token=token)
        else:
            result = handle_internal_recommendation(payload, internal_token=token)
        await _send_json(send, _json_status(result), result)
        return

    await _send_json(send, 404, {"error": "not_found", "path": path})


def _headers(scope: dict[str, Any]) -> dict[str, str]:
    return {
        key.decode("latin-1").lower(): value.decode("latin-1")
        for key, value in scope.get("headers", [])
    }


async def _read_json(receive: Any) -> dict[str, Any]:
    body = bytearray()
    more_body = True
    while more_body:
        message = await receive()
        body.extend(message.get("body", b""))
        more_body = bool(message.get("more_body", False))
    if not body:
        return {}
    try:
        parsed = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


async def _send_json(send: Any, status_code: int, payload: dict[str, Any]) -> None:
    body = json.dumps(payload, default=str).encode("utf-8")
    await send(
        {
            "type": "http.response.start",
            "status": status_code,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode("ascii")),
            ],
        }
    )
    await send({"type": "http.response.body", "body": body})


async def _send_text(send: Any, status_code: int, content_type: str, body: str) -> None:
    encoded = body.encode("utf-8")
    await send(
        {
            "type": "http.response.start",
            "status": status_code,
            "headers": [
                (b"content-type", content_type.encode("ascii")),
                (b"content-length", str(len(encoded)).encode("ascii")),
            ],
        }
    )
    await send({"type": "http.response.body", "body": encoded})


def _json_status(result: dict[str, Any]) -> int:
    if result.get("ok"):
        return 200
    code = str((result.get("error") or {}).get("code") or "")
    if code == "unauthorized_internal_request":
        return 401
    if code in {"invalid_request", "dependency_contract_error"}:
        return 422
    if code in {"dependency_unavailable", "dependency_timeout"}:
        return 503
    return 500


async def _send_sse(send: Any, payload: dict[str, Any], *, internal_token: str | None) -> None:
    """Run the internal stream and emit one safe SSE frame per event."""
    settings = get_settings()
    try:
        validate_internal_token(internal_token, settings)
        request = agent_request_from_payload(payload)
        service = OrchestrationService(settings=settings)
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [
                    (b"content-type", b"text/event-stream; charset=utf-8"),
                    (b"cache-control", b"no-cache"),
                    (b"x-accel-buffering", b"no"),
                    (b"connection", b"keep-alive"),
                ],
            }
        )
        for event in service.stream(request):
            frame = f"event: {event['event']}\ndata: {json.dumps(event, default=str)}\n\n".encode("utf-8")
            await send({"type": "http.response.body", "body": frame, "more_body": True})
        await send({"type": "http.response.body", "body": b"", "more_body": False})
    except AgentsError as exc:
        envelope = {"ok": False, "error": exc.envelope().to_dict()}
        frame = f"event: error\ndata: {json.dumps(envelope)}\n\n".encode("utf-8")
        await send(
            {
                "type": "http.response.start",
                "status": 401 if exc.code == "unauthorized_internal_request" else 400,
                "headers": [(b"content-type", b"text/event-stream; charset=utf-8")],
            }
        )
        await send({"type": "http.response.body", "body": frame})
    except Exception:
        frame = b'event: error\ndata: {"ok":false,"error":{"code":"agents_internal_error","message":"Agents request failed safely."}}\n\n'
        await send(
            {
                "type": "http.response.start",
                "status": 500,
                "headers": [(b"content-type", b"text/event-stream; charset=utf-8")],
            }
        )
        await send({"type": "http.response.body", "body": frame})


__all__ = [
    "app",
    "app_routes",
    "handle_internal_chat",
    "handle_internal_recommendation",
    "health_live",
    "health_ready",
]
