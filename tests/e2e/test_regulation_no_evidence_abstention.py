"""E2E journey: regulation intent tapi RAG tidak mengembalikan citation apa
pun -> guardrail wajib memaksa abstain, bukan menjawab tanpa dasar hukum.
"""

from tests.e2e._support import build_service, make_request, regulation_retrieve_no_citation


def test_regulation_chat_abstains_without_citation() -> None:
    service = build_service(retrieve_func=regulation_retrieve_no_citation)
    request = make_request(query="apa syarat dokumen ekspor", requested_intent="regulation")

    response = service.handle(request)

    assert response.intent == "regulation"
    assert response.abstained is True
    assert response.answer_available is False
    assert response.citations == []
    assert "citation" in (response.abstention_reason or "").casefold()