from __future__ import annotations

import json
import logging
from typing import Any

SENSITIVE_KEYS = {"password", "secret", "token", "api_key", "authorization"}


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: "***REDACTED***" if key.casefold() in SENSITIVE_KEYS else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def get_logger(name: str = "opticargo.agents") -> logging.Logger:
    return logging.getLogger(name)


def log_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    logger.info(json.dumps({"event": event, **redact(fields)}, default=str))


__all__ = ["SENSITIVE_KEYS", "get_logger", "log_event", "redact"]
