from __future__ import annotations

from dataclasses import replace

from opticargo_agents.contracts import RetrievalRequest, RetrievalResult
from opticargo_agents.integrations import RagAdapter

_NO_CITATION_REASON = "Retrieved evidence has no citation; abstaining to avoid an ungrounded answer."


def run_retrieval_node(request: RetrievalRequest, adapter: RagAdapter) -> RetrievalResult:
    result = adapter.retrieve(request)

    if result.abstained:
        return result

    if not result.citations:
        return replace(
            result,
            abstained=True,
            abstention_reason=_NO_CITATION_REASON,
            warnings=[*result.warnings, "Forced abstention: retrieval result had no citation."],
        )

    return result


__all__ = ["run_retrieval_node"]