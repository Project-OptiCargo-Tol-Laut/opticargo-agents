from __future__ import annotations

from opticargo_agents.contracts import GraphContextResult, MLScoreResult, RetrievalResult, SynthesisResult

_NO_EVIDENCE_REASON = "No evidence was gathered from retrieval, graph analysis, or optimization."
_RETRIEVAL_ABSTAINED_REASON = "Retrieval evidence was insufficient."
_GRAPH_UNAVAILABLE_REASON = "Knowledge graph context is unavailable."
_ML_UNAVAILABLE_REASON = "Cargo scoring is unavailable."


def run_synthesis_node(
    *,
    retrieval: RetrievalResult | None = None,
    graph_context: GraphContextResult | None = None,
    ml_score: MLScoreResult | None = None,
) -> SynthesisResult:
    if retrieval is None and graph_context is None and ml_score is None:
        return SynthesisResult(abstained=True, abstention_reason=_NO_EVIDENCE_REASON)

    if retrieval is not None and retrieval.abstained:
        return SynthesisResult(
            abstained=True,
            abstention_reason=retrieval.abstention_reason or _RETRIEVAL_ABSTAINED_REASON,
            warnings=list(retrieval.warnings),
        )

    if graph_context is not None and not graph_context.available:
        return SynthesisResult(
            abstained=True,
            abstention_reason=_GRAPH_UNAVAILABLE_REASON,
            warnings=list(graph_context.warnings),
        )

    if ml_score is not None and not ml_score.available:
        return SynthesisResult(
            abstained=True,
            abstention_reason=_ML_UNAVAILABLE_REASON,
            warnings=list(ml_score.warnings),
        )

    citations = list(retrieval.citations) if retrieval is not None else []
    requires_human_confirmation = ml_score is not None and ml_score.available

    return SynthesisResult(
        answer_available=True,
        citations=citations,
        requires_human_confirmation=requires_human_confirmation,
        abstained=False,
    )


__all__ = ["run_synthesis_node"]