"""E2E journey: regulation intent -> retrieval -> synthesis, dengan citation
yang valid dari RAG. Memastikan jawaban benar-benar melampirkan citation
dan tidak pernah requires_human_confirmation (bukan aksi operasional).
"""

from tests.e2e._support import build_service, make_request, regulation_retrieve


def test_regulation_chat_answers_with_citation() -> None:
    service = build_service(retrieve_func=regulation_retrieve)
    request = make_request(query="apa syarat sertifikasi muatan balik tol laut", requested_intent="regulation")

    response = service.handle(request)

    assert response.intent == "regulation"
    assert response.route == ["intent", "retrieval", "synthesis"]
    assert response.abstained is False
    assert response.answer_available is True
    assert len(response.citations) >= 1
    assert response.citations[0]["document_id"] == "PM-99-2023"
    assert response.requires_human_confirmation is False