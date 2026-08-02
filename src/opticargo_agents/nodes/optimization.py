from __future__ import annotations

from typing import Any

from opticargo_agents.clients import MLModelsClient
from opticargo_agents.contracts import MLScoreResult


def run_cargo_scoring_node(
    payload: dict[str, Any],
    client: MLModelsClient,
    *,
    correlation_id: str | None = None,
) -> MLScoreResult:
    return client.score_cargo_match(payload, correlation_id=correlation_id)


__all__ = ["run_cargo_scoring_node"]
