from __future__ import annotations

from opticargo_agents.health import liveness_report, readiness_report


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


__all__ = ["app_routes", "health_live", "health_ready"]
