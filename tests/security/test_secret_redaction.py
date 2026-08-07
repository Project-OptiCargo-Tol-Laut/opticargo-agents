"""Security: pastikan `redact()` menyembunyikan semua field sensitif secara
rekursif (nested dict, list of dict), case-insensitive, tanpa mengubah field
non-sensitif.

Rujukan: src/opticargo_agents/logging.py (SENSITIVE_KEYS, redact)
"""

from opticargo_agents.logging import SENSITIVE_KEYS, redact


def test_redact_masks_top_level_sensitive_keys() -> None:
    payload = {"token": "abc123", "password": "hunter2", "correlation_id": "req-1"}
    result = redact(payload)

    assert result["token"] == "***REDACTED***"
    assert result["password"] == "***REDACTED***"
    assert result["correlation_id"] == "req-1"


def test_redact_is_case_insensitive() -> None:
    payload = {"TOKEN": "abc123", "Api_Key": "xyz", "Authorization": "Bearer xyz"}
    result = redact(payload)

    assert result["TOKEN"] == "***REDACTED***"
    assert result["Api_Key"] == "***REDACTED***"
    assert result["Authorization"] == "***REDACTED***"


def test_redact_masks_nested_dict_values() -> None:
    payload = {"request": {"headers": {"token": "abc123"}, "path": "/internal/v1/chat"}}
    result = redact(payload)

    assert result["request"]["headers"]["token"] == "***REDACTED***"
    assert result["request"]["path"] == "/internal/v1/chat"


def test_redact_masks_secrets_inside_list_of_dicts() -> None:
    payload = {"attempts": [{"secret": "s1"}, {"secret": "s2", "status": "failed"}]}
    result = redact(payload)

    assert result["attempts"][0]["secret"] == "***REDACTED***"
    assert result["attempts"][1]["secret"] == "***REDACTED***"
    assert result["attempts"][1]["status"] == "failed"


def test_all_documented_sensitive_keys_are_actually_redacted() -> None:
    payload = {key: "sensitive-value" for key in SENSITIVE_KEYS}
    result = redact(payload)

    for key in SENSITIVE_KEYS:
        assert result[key] == "***REDACTED***", f"{key} was not redacted"