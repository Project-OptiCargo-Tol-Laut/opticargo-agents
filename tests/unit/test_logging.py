from opticargo_agents.logging import redact


def test_redact_masks_sensitive_keys_recursively() -> None:
    payload = {"token": "abc", "nested": {"password": "secret"}, "safe": "ok"}

    assert redact(payload) == {
        "token": "***REDACTED***",
        "nested": {"password": "***REDACTED***"},
        "safe": "ok",
    }
