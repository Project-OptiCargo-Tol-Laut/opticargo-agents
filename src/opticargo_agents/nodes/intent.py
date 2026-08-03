from __future__ import annotations

from collections.abc import Callable

from opticargo_agents.contracts import IntentResult

CANONICAL_INTENTS = {"regulation", "matching", "route", "analytics", "unknown"}
_MIN_HEURISTIC_CONFIDENCE = 0.55

_KEYWORDS: dict[str, tuple[str, ...]] = {
    "regulation": (
        "aturan",
        "regulasi",
        "peraturan",
        "hukum",
        "izin",
        "syarat",
        "dokumen",
        "sertifikat",
        "kebijakan",
        "larangan",
        "ketentuan",
    ),
    "matching": (
        "matching",
        "cocok",
        "muatan",
        "kargo",
        "supplier",
        "pemasok",
        "kapal",
        "rekomendasi",
        "backhaul",
        "angkut",
    ),
    "route": (
        "rute",
        "route",
        "pelabuhan",
        "jalur",
        "voyage",
        "perjalanan",
        "singgah",
        "origin",
        "destination",
        "tujuan",
    ),
    "analytics": (
        "analitik",
        "analytics",
        "analisis",
        "statistik",
        "overview",
        "ringkasan",
        "performa",
        "tren",
        "utilisasi",
        "laporan",
    ),
}


LLMIntentClassifier = Callable[[str], str | IntentResult | dict[str, object] | None]


def run_intent_node(
    query: str,
    *,
    requested_intent: str | None = None,
    llm_classifier: LLMIntentClassifier | None = None,
) -> IntentResult:
    requested = _normalize_intent(requested_intent)
    if requested != "unknown":
        return IntentResult(
            intent=requested,
            confidence=1.0,
            source="request",
            rationale="Valid intent was supplied by the caller.",
        )

    heuristic = _classify_with_keywords(query)
    if heuristic.intent != "unknown" and heuristic.confidence >= _MIN_HEURISTIC_CONFIDENCE:
        return heuristic

    if llm_classifier is not None:
        llm_result = _coerce_llm_result(llm_classifier(query))
        if llm_result.intent != "unknown":
            return llm_result

    return heuristic


def _normalize_intent(value: str | None) -> str:
    if value is None:
        return "unknown"
    normalized = value.strip().lower().replace("-", "_")
    return normalized if normalized in CANONICAL_INTENTS else "unknown"


def _classify_with_keywords(query: str) -> IntentResult:
    text = f" {query.strip().lower()} "
    if not text.strip():
        return IntentResult(intent="unknown", confidence=0.0, rationale="Query is empty.")

    scores = {
        intent: sum(1 for keyword in keywords if keyword in text)
        for intent, keywords in _KEYWORDS.items()
    }
    best_intent, best_score = max(scores.items(), key=lambda item: (item[1], item[0]))
    if best_score <= 0:
        return IntentResult(
            intent="unknown",
            confidence=0.0,
            rationale="No deterministic intent keyword matched the query.",
        )

    total = sum(scores.values())
    confidence = min(0.95, 0.5 + (best_score / max(total, 1)) * 0.45)
    return IntentResult(
        intent=best_intent,
        confidence=confidence,
        rationale=f"Matched {best_score} deterministic keyword(s).",
    )


def _coerce_llm_result(value: str | IntentResult | dict[str, object] | None) -> IntentResult:
    if isinstance(value, IntentResult):
        intent = _normalize_intent(value.intent)
        return IntentResult(
            intent=intent,
            confidence=value.confidence if intent != "unknown" else 0.0,
            source="llm",
            rationale=value.rationale,
        )
    if isinstance(value, dict):
        intent = _normalize_intent(str(value.get("intent", "")))
        confidence = value.get("confidence", 0.0)
        return IntentResult(
            intent=intent,
            confidence=float(confidence) if intent != "unknown" else 0.0,
            source="llm",
            rationale=str(value.get("rationale")) if value.get("rationale") else None,
        )
    intent = _normalize_intent(value if isinstance(value, str) else None)
    return IntentResult(intent=intent, confidence=0.75 if intent != "unknown" else 0.0, source="llm")


__all__ = ["CANONICAL_INTENTS", "LLMIntentClassifier", "run_intent_node"]
