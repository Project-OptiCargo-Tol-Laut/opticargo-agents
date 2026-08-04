from __future__ import annotations

from collections.abc import Callable
import re

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
        "karantina",
        "legalitas",
        "kepatuhan",
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
        "kandidat",
        "kapasitas kosong",
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
        "jarak",
        "estimasi",
        "trayek",
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
        "berapa banyak",
        "total",
    ),
}

_PHRASE_BOOSTS: dict[str, tuple[str, ...]] = {
    "regulation": ("apa syarat", "dasar hukum", "wajib dokumen", "sesuai aturan"),
    "matching": ("muatan balik", "kargo balik", "cari supplier", "rekomendasi muatan"),
    "route": ("dari mana", "ke mana", "jelaskan rute", "berapa jauh"),
    "analytics": ("buat ringkasan", "berapa total", "berapa banyak", "dashboard"),
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
    text = " ".join(query.strip().casefold().split())
    if not text.strip():
        return IntentResult(intent="unknown", confidence=0.0, rationale="Query is empty.")

    scores = {
        intent: sum(_keyword_weight(text, keyword) for keyword in keywords)
        + sum(2 for phrase in _PHRASE_BOOSTS[intent] if phrase in text)
        for intent, keywords in _KEYWORDS.items()
    }
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    best_intent, best_score = ranked[0]
    if best_score <= 0:
        return IntentResult(
            intent="unknown",
            confidence=0.0,
            rationale="No deterministic intent keyword matched the query.",
        )

    runner_up_score = ranked[1][1]
    total = sum(scores.values())
    margin = best_score - runner_up_score
    confidence = min(0.95, 0.5 + (best_score / max(total, 1)) * 0.35 + min(margin, 3) * 0.04)
    return IntentResult(
        intent=best_intent,
        confidence=confidence,
        rationale=f"Matched deterministic signals with score {best_score} and margin {margin}.",
    )


def _keyword_weight(text: str, keyword: str) -> int:
    """Match complete Indonesian words/phrases, avoiding accidental substrings."""
    pattern = rf"(?<!\w){re.escape(keyword)}(?!\w)"
    return 1 if re.search(pattern, text) else 0


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
