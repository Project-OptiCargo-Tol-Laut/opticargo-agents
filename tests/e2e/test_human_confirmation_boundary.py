"""E2E journey: memastikan boundary human-confirmation ditegakkan dengan
benar di seluruh intent -- hanya `matching` (rekomendasi operasional) yang
mewajibkan konfirmasi manusia, dan jawabannya tidak pernah mengklaim
transaksi/booking sudah selesai.
"""

from tests.e2e._support import (
    build_service,
    make_request,
    regulation_retrieve,
    successful_ml_response,
    voyage_graph_context,
)

_MUTATION_PHRASES = ("booking berhasil", "pembayaran berhasil", "transaksi selesai", "status booking diubah")


def test_matching_requires_human_confirmation_and_never_claims_transaction() -> None:
    service = build_service(
        graph_query_func=lambda session, **kwargs: voyage_graph_context(),
        ml_response=successful_ml_response(),
    )
    response = service.handle(make_request(query="matching", requested_intent="matching"))

    assert response.requires_human_confirmation is True
    answer = (response.answer or "").casefold()
    assert not any(phrase in answer for phrase in _MUTATION_PHRASES)


def test_regulation_answer_does_not_require_human_confirmation() -> None:
    service = build_service(retrieve_func=regulation_retrieve)
    response = service.handle(make_request(query="regulation", requested_intent="regulation"))

    assert response.requires_human_confirmation is False


def test_route_answer_does_not_require_human_confirmation() -> None:
    service = build_service(graph_query_func=lambda session, **kwargs: voyage_graph_context())
    response = service.handle(make_request(query="route", requested_intent="route"))

    assert response.requires_human_confirmation is False