"""E2E journey: matching intent tapi Knowledge Graph tidak punya kandidat
kargo balik apapun -> synthesis wajib abstain, bukan mengarang jawaban.
"""

from tests.e2e._support import build_service, make_request, voyage_graph_context


def test_matching_abstains_when_no_candidates_available() -> None:
    service = build_service(
        graph_query_func=lambda session, **kwargs: voyage_graph_context(candidates=[]),
    )
    request = make_request(query="cari muatan balik", requested_intent="matching")

    response = service.handle(request)

    assert response.intent == "matching"
    assert response.abstained is True
    assert response.answer_available is False
    assert "kandidat" in (response.abstention_reason or "").casefold()
    assert response.requires_human_confirmation is False