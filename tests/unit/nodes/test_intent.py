from opticargo_agents.contracts import IntentResult
from opticargo_agents.nodes.intent import run_intent_node


def test_intent_node_uses_valid_requested_intent_first() -> None:
    result = run_intent_node("apa saja", requested_intent="matching")

    assert result.intent == "matching"
    assert result.confidence == 1.0
    assert result.source == "request"


def test_intent_node_ignores_invalid_requested_intent() -> None:
    result = run_intent_node("apa syarat dokumen tol laut?", requested_intent="random")

    assert result.intent == "regulation"
    assert result.source == "heuristic"


def test_intent_node_classifies_matching_keywords() -> None:
    result = run_intent_node("rekomendasi muatan backhaul untuk kapal ini")

    assert result.intent == "matching"
    assert result.confidence >= 0.55


def test_intent_node_classifies_route_keywords() -> None:
    result = run_intent_node("cek rute kapal dari pelabuhan asal ke tujuan")

    assert result.intent == "route"


def test_intent_node_classifies_analytics_keywords() -> None:
    result = run_intent_node("buat ringkasan analitik utilisasi kapal")

    assert result.intent == "analytics"


def test_intent_node_prefers_matching_for_indonesian_backhaul_phrase() -> None:
    result = run_intent_node("carikan supplier untuk muatan balik kapal ini")

    assert result.intent == "matching"


def test_intent_node_does_not_match_keyword_inside_unrelated_word() -> None:
    result = run_intent_node("kapalkan barang ini besok")

    assert result.intent == "unknown"


def test_intent_node_preserves_unknown_when_no_signal() -> None:
    result = run_intent_node("halo apa kabar")

    assert result.intent == "unknown"
    assert result.confidence == 0.0


def test_intent_node_accepts_valid_llm_fallback_only() -> None:
    result = run_intent_node("tolong bantu ini", llm_classifier=lambda query: "route")

    assert result.intent == "route"
    assert result.source == "llm"


def test_intent_node_rejects_invalid_llm_fallback() -> None:
    result = run_intent_node("tolong bantu ini", llm_classifier=lambda query: IntentResult(intent="booking"))

    assert result.intent == "unknown"
