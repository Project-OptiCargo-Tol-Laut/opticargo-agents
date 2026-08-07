"""Security: pastikan `log_event` (jalur log resmi) benar-benar menerapkan
redaction sebelum menulis JSON log -- bukan cuma `redact()` yang teruji
terpisah, tapi jalur pemanggilannya juga.

Rujukan: src/opticargo_agents/logging.py (log_event)
"""

import json
import logging

from opticargo_agents.logging import get_logger, log_event


class _CapturingHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record.getMessage())


def _logger_with_capture() -> tuple[logging.Logger, _CapturingHandler]:
    logger = get_logger("opticargo.agents.test_log_allowlist")
    logger.setLevel(logging.INFO)
    handler = _CapturingHandler()
    logger.addHandler(handler)
    logger.propagate = False
    return logger, handler


def test_log_event_redacts_sensitive_fields_before_writing() -> None:
    logger, handler = _logger_with_capture()

    log_event(logger, "internal_request", token="super-secret-token", path="/internal/v1/chat")

    assert len(handler.records) == 1
    parsed = json.loads(handler.records[0])
    assert parsed["event"] == "internal_request"
    assert parsed["token"] == "***REDACTED***"
    assert parsed["path"] == "/internal/v1/chat"
    assert "super-secret-token" not in handler.records[0]


def test_log_event_redacts_nested_sensitive_fields() -> None:
    logger, handler = _logger_with_capture()

    log_event(
        logger,
        "dependency_call",
        request={"headers": {"authorization": "Bearer secret-xyz"}, "url": "http://ml-models:8000"},
    )

    raw = handler.records[0]
    parsed = json.loads(raw)
    assert parsed["request"]["headers"]["authorization"] == "***REDACTED***"
    assert "secret-xyz" not in raw