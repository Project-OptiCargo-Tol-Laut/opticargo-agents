from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LLMResult:
    text: str
    fallback_used: bool = True
    warning: str | None = None


class LLMClient:
    """Optional LLM boundary.

    The baseline intentionally returns deterministic fallback so runtime does
    not depend on an external model provider.
    """

    def complete(self, prompt: str, *, correlation_id: str | None = None) -> LLMResult:
        _ = (prompt, correlation_id)
        return LLMResult(text="", fallback_used=True, warning="LLM is not configured.")


__all__ = ["LLMClient", "LLMResult"]
