"""E2E journey: matching intent -> graph -> optimization -> retrieval ->
synthesis, end-to-end melalui OrchestrationService.handle() dengan adapter
palsu deterministik (bukan mock node).

Evidence: node route, ownership boundary (wajib human confirmation, tidak
pernah klaim transaksi selesai).
"""

from tests.e2e._support import build_service, make_request, successful_ml_response, voyage_graph_context


def test_matching_recommendation_returns_answer_with_human_confirmation_required() -> None:
    service = build_service(
        graph_query_func=lambda session, **kwargs: voyage_graph_context(),
        ml_response=successful_ml_response(score=0.82, hard_constraint_valid=True),
    )
    request = make_request(query="cari muatan balik dari Makassar", requested_intent="matching")

    response = service.handle(request)

    assert response.intent == "matching"
    assert response.route == ["intent", "graph", "optimization", "retrieval", "synthesis"]
    assert response.abstained is False
    assert response.answer_available is True
    assert response.requires_human_confirmation is True
    assert "belum melakukan booking" in (response.answer or "")


def test_matching_recommendation_trace_records_every_node_in_route() -> None:
    service = build_service(
        graph_query_func=lambda session, **kwargs: voyage_graph_context(),
        ml_response=successful_ml_response(),
    )
    request = make_request(query="matching", requested_intent="matching")

    response = service.handle(request)

    traced_nodes = [item["node"] for item in response.trace]
    assert traced_nodes == ["intent", "graph", "optimization", "retrieval", "synthesis"]