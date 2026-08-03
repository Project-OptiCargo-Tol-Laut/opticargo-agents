from opticargo_agents.config import load_settings
from opticargo_agents.errors import UnauthorizedInternalRequestError
from opticargo_agents.security import validate_internal_token


def test_validate_internal_token_allows_development_without_secret() -> None:
    validate_internal_token(None, load_settings({"OPTICARGO_ENVIRONMENT": "development"}))


def test_validate_internal_token_accepts_matching_secret() -> None:
    settings = load_settings(
        {"OPTICARGO_ENVIRONMENT": "production", "INTERNAL_SERVICE_TOKEN": "secret"}
    )

    validate_internal_token("secret", settings)


def test_validate_internal_token_rejects_invalid_secret() -> None:
    settings = load_settings(
        {"OPTICARGO_ENVIRONMENT": "production", "INTERNAL_SERVICE_TOKEN": "secret"}
    )

    try:
        validate_internal_token("wrong", settings)
    except UnauthorizedInternalRequestError:
        return
    raise AssertionError("Invalid internal token was accepted.")
