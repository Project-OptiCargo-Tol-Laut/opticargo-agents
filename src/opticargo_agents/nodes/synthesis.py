from __future__ import annotations

from typing import Any

from opticargo_agents.contracts import GraphContextResult, MLScoreResult, RetrievalResult, SynthesisResult
from opticargo_agents.guardrails import (
    validate_citations_present_when_required,
    validate_no_transaction_claim,
)

_NO_EVIDENCE_REASON = "Tidak ada evidence dari retrieval, graph, atau scoring."
_GRAPH_UNAVAILABLE_REASON = "Konteks Knowledge Graph tidak tersedia."


def run_synthesis_node(
    *,
    retrieval: RetrievalResult | None = None,
    graph_context: GraphContextResult | None = None,
    ml_score: MLScoreResult | None = None,
) -> SynthesisResult:
    intent = _infer_intent(retrieval, graph_context, ml_score)
    warnings = _warnings(retrieval, graph_context, ml_score)
    citations: list[dict[str, Any]] = []

    if intent == "unknown":
        return SynthesisResult(
            abstained=True,
            abstention_reason=_NO_EVIDENCE_REASON,
            warnings=warnings,
        )

    if intent == "regulation":
        if retrieval is None or retrieval.abstained or not retrieval.citations:
            return SynthesisResult(
                abstained=True,
                abstention_reason=(
                    retrieval.abstention_reason
                    if retrieval is not None and retrieval.abstention_reason
                    else "Evidence regulasi dengan citation tidak tersedia."
                ),
                warnings=warnings,
            )
        citations = _primary_regulation_citations(retrieval.citations)
        answer = _regulation_answer(citations)
    else:
        if graph_context is None or not graph_context.available:
            return SynthesisResult(
                abstained=True,
                abstention_reason=_GRAPH_UNAVAILABLE_REASON,
                warnings=warnings,
            )
        if intent == "matching":
            candidates = _candidates(graph_context)
            if not candidates:
                return SynthesisResult(
                    abstained=True,
                    abstention_reason="Tidak ada kandidat muatan balik yang memenuhi konteks voyage.",
                    warnings=warnings,
                )
            answer = _matching_answer(graph_context, ml_score)
        elif intent == "route":
            answer = _route_answer(graph_context)
        else:
            answer = _analytics_answer(graph_context)

    # Citation regulation must not leak into operational route/matching answers.
    requires_human_confirmation = intent == "matching"

    transaction_guard = validate_no_transaction_claim(answer)
    if not transaction_guard.allowed:
        return SynthesisResult(
            abstained=True,
            abstention_reason=transaction_guard.reason,
            warnings=warnings,
        )

    citation_guard = validate_citations_present_when_required(
        {"intent": intent, "citations": citations, "abstained": False}
    )
    if not citation_guard.allowed:
        return SynthesisResult(
            abstained=True,
            abstention_reason=citation_guard.reason,
            warnings=warnings,
        )

    return SynthesisResult(
        answer=answer,
        answer_available=bool(answer),
        citations=citations,
        requires_human_confirmation=requires_human_confirmation,
        abstained=False,
        warnings=warnings,
    )


def _infer_intent(
    retrieval: RetrievalResult | None,
    graph_context: GraphContextResult | None,
    ml_score: MLScoreResult | None,
) -> str:
    if ml_score is not None:
        return "matching"
    if graph_context is not None and retrieval is not None:
        return "route"
    if graph_context is not None:
        return "analytics"
    if retrieval is not None:
        return "regulation"
    return "unknown"


def _warnings(
    retrieval: RetrievalResult | None,
    graph_context: GraphContextResult | None,
    ml_score: MLScoreResult | None,
) -> list[str]:
    values: list[str] = []
    for item in (retrieval, graph_context, ml_score):
        if item is not None:
            values.extend(item.warnings)
    return list(dict.fromkeys(values))


def _context(graph_context: GraphContextResult) -> dict[str, Any]:
    return graph_context.context or {}


def _candidates(graph_context: GraphContextResult) -> list[dict[str, Any]]:
    values = _context(graph_context).get("candidates") or []
    return [value for value in values if isinstance(value, dict)]


def _primary_regulation_citations(citations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep answer evidence on the highest-ranked regulation document."""
    if not citations:
        return []
    first = citations[0]
    primary_key = str(first.get("document_id") or first.get("title") or "")
    if not primary_key:
        return [first]
    primary = [
        citation
        for citation in citations
        if str(citation.get("document_id") or citation.get("title") or "") == primary_key
    ]
    return primary[:3] or [first]


def _regulation_answer(citations: list[dict[str, Any]]) -> str:
    lines = [
        "Berikut dasar regulasi yang paling relevan dari dokumen resmi yang terindeks:"
    ]
    for index, citation in enumerate(citations[:3], start=1):
        title = str(citation.get("title") or "Dokumen regulasi")
        page = citation.get("page")
        location = f", halaman {page}" if page is not None else ""
        excerpt = " ".join(str(citation.get("excerpt") or "").split())
        if len(excerpt) > 360:
            excerpt = excerpt[:357].rstrip() + "..."
        lines.append(f"{index}. {title}{location}: {excerpt}")
    lines.append(
        "Gunakan citation terlampir untuk memeriksa bunyi pasal lengkap sebelum mengambil keputusan operasional."
    )
    return "\n".join(lines)


def _matching_answer(
    graph_context: GraphContextResult,
    ml_score: MLScoreResult | None,
) -> str:
    candidate = _candidates(graph_context)[0]
    supplier = candidate.get("supplier") or {}
    supplier_name = supplier.get("supplier_name") or "supplier kandidat"
    commodity = candidate.get("commodity_name") or "komoditas"
    weight = candidate.get("available_weight_ton") or "tidak diketahui"
    scoring_available = ml_score is not None and ml_score.available
    score = float(ml_score.score or 0) if ml_score is not None else 0.0
    mode = ml_score.model_mode or "unknown" if ml_score is not None else "unavailable"
    fallback = (
        " Skor ini memakai heuristic fallback karena model terlatih belum tersedia."
        if ml_score is not None and ml_score.fallback_used and scoring_available
        else ""
    )
    scoring_text = (
        f"Skor kecocokan {score:.3f} dalam mode {mode}.{fallback}"
        if scoring_available
        else "Scoring ML tidak tersedia; kandidat ini dipilih dari kecocokan dan kapasitas Knowledge Graph saja."
    )
    return (
        f"Kandidat utama adalah {supplier_name} untuk komoditas {commodity}, "
        f"dengan volume tersedia sekitar {weight} ton. {scoring_text} "
        "Rekomendasi ini belum melakukan booking atau "
        "perubahan transaksi dan wajib dikonfirmasi manusia sebelum ditindaklanjuti."
    )


def _route_answer(graph_context: GraphContextResult) -> str:
    context = _context(graph_context)
    leg = context.get("active_leg") or {}
    origin = (leg.get("origin_port") or {}).get("name") or "pelabuhan asal"
    destination = (leg.get("destination_port") or {}).get("name") or "pelabuhan tujuan"
    distance = leg.get("distance_nm")
    estimated_days = leg.get("estimated_days")
    capacity = context.get("ship_capacity") or {}
    remaining = capacity.get("remaining_weight_ton")
    candidate_count = len(_candidates(graph_context))
    return (
        f"Voyage bergerak dari {origin} menuju {destination}"
        f"{f' sejauh {distance} mil laut' if distance is not None else ''}"
        f"{f' dengan estimasi {estimated_days} hari' if estimated_days is not None else ''}. "
        f"Sisa kapasitas tercatat {remaining or 'tidak diketahui'} ton dan terdapat "
        f"{candidate_count} kandidat muatan pada konteks tujuan."
    )


def _analytics_answer(graph_context: GraphContextResult) -> str:
    candidates = _candidates(graph_context)
    supplier_ids = {
        str((candidate.get("supplier") or {}).get("supplier_id"))
        for candidate in candidates
        if (candidate.get("supplier") or {}).get("supplier_id")
    }
    commodities = sorted(
        {
            str(candidate.get("commodity_name"))
            for candidate in candidates
            if candidate.get("commodity_name")
        }
    )
    total_weight = sum(_float(candidate.get("available_weight_ton")) for candidate in candidates)
    commodity_text = ", ".join(commodities[:5]) if commodities else "belum ada"
    return (
        f"Knowledge Graph menemukan {len(supplier_ids)} supplier unik dan "
        f"{len(candidates)} kombinasi kandidat, dengan total potensi sekitar "
        f"{total_weight:.2f} ton. Komoditas teratas: {commodity_text}."
    )


def _float(value: object) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0


__all__ = ["run_synthesis_node"]
