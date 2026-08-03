from __future__ import annotations

from dataclasses import replace
from typing import Any

from opticargo_agents.clients import MLModelsClient
from opticargo_agents.contracts import MLScoreResult
from opticargo_agents.errors import HardConstraintViolationError

_HARD_CONSTRAINT_REASON = "Cargo candidate failed a hard constraint check; excluding from ranking."


def run_cargo_scoring_node(
    payload: dict[str, Any],
    client: MLModelsClient,
    *,
    correlation_id: str | None = None,
) -> MLScoreResult:
    result = client.score_cargo_match(payload, correlation_id=correlation_id)

    if result.error is not None:
        return result

    if result.hard_constraint_valid is False:
        error = HardConstraintViolationError(_HARD_CONSTRAINT_REASON, dependency="ml_models")
        return replace(
            result,
            score=None,
            error=error.envelope(),
            warnings=[*result.warnings, "Forced exclusion: hard_constraint_valid is False."],
        )

    return result


__all__ = ["run_cargo_scoring_node"]