from __future__ import annotations

import secrets

from opticargo_agents.config import Settings, get_settings
from opticargo_agents.errors import UnauthorizedInternalRequestError


def validate_internal_token(
    provided_token: str | None,
    settings: Settings | None = None,
) -> None:
    active_settings = settings or get_settings()
    expected = active_settings.internal_service_token
    if not expected and active_settings.environment == "development":
        return
    if not expected:
        raise UnauthorizedInternalRequestError("INTERNAL_SERVICE_TOKEN is not configured.")
    if not provided_token or not secrets.compare_digest(provided_token, expected):
        raise UnauthorizedInternalRequestError("Invalid internal service token.")


__all__ = ["validate_internal_token"]
