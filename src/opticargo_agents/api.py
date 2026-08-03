from __future__ import annotations

from typing import Any

from opticargo_agents.config import Settings, get_settings
from opticargo_agents.contracts import agent_request_from_payload
from opticargo_agents.errors import AgentsError
from opticargo_agents.health import liveness_report, readiness_report
from opticargo_agents.orchestrator import OrchestrationService
from opticargo_agents.security import validate_internal_token


def app_routes() -> dict[str, str]:
    return {
        "liveness": "/health/live",
        "readiness": "/health/ready",
        "recommendation": "/internal/v1/recommendations",
        "chat": "/internal/v1/chat",
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
    enriched_payload = {"requested_intent": "matching", **payload}
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


__all__ = [
    "app_routes",
    "handle_internal_chat",
    "handle_internal_recommendation",
    "health_live",
    "health_ready",
]
