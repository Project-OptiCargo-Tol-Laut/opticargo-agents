"""Security: pastikan seluruh internal endpoint menolak request tanpa token
valid, dan menerima request dengan token yang benar.

Rujukan: docs/SECURITY_BOUNDARY.md
"""

from opticargo_agents.api import handle_internal_chat
from opticargo_agents.config import load_settings
from opticargo_agents.errors import UnauthorizedInternalRequestError
from opticargo_agents.security import validate_internal_token


def _production_settings(token: str = "correct-token-abc") -> object:
    return load_settings({"OPTICARGO_ENVIRONMENT": "production", "INTERNAL_SERVICE_TOKEN": token})


def test_validate_internal_token_rejects_missing_token_in_production() -> None:
    settings = _production_settings()
    try:
        validate_internal_token(None, settings)
        assert False, "Expected UnauthorizedInternalRequestError"
    except UnauthorizedInternalRequestError:
        pass


def test_validate_internal_token_rejects_empty_string_token() -> None:
    settings = _production_settings()
    try:
        validate_internal_token("", settings)
        assert False, "Expected UnauthorizedInternalRequestError"
    except UnauthorizedInternalRequestError:
        pass


def test_validate_internal_token_accepts_correct_token() -> None:
    settings = _production_settings("correct-token-abc")
    validate_internal_token("correct-token-abc", settings)  # must not raise


def test_handle_internal_chat_returns_unauthorized_envelope_without_token() -> None:
    settings = _production_settings()
    response = handle_internal_chat({"message": "halo"}, settings=settings)

    assert response["ok"] is False
    assert response["error"]["code"] == "unauthorized_internal_request"


def test_missing_token_is_allowed_only_in_development_without_configured_secret() -> None:
    dev_settings = load_settings({"OPTICARGO_ENVIRONMENT": "development", "INTERNAL_SERVICE_TOKEN": ""})
    validate_internal_token(None, dev_settings)  # must not raise: local dev convenience only

    prod_settings = load_settings({"OPTICARGO_ENVIRONMENT": "production", "INTERNAL_SERVICE_TOKEN": ""})
    try:
        validate_internal_token(None, prod_settings)
        assert False, "Production without a configured secret must still reject requests"
    except UnauthorizedInternalRequestError:
        pass