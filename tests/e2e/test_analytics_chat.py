"""E2E journey: analytics intent -> graph -> synthesis (tanpa retrieval,
tanpa optimization). Menjawab ringkasan analitik dari Knowledge Graph saja.
"""

from tests.e2e._support import build_service, make_request, voyage_graph_context


def test_analytics_chat_summarizes_graph_context() -> None:
    service = build_service(graph_query_func=lambda session, **kwargs: voyage_graph_context())
    request = make_request(query="berapa banyak supplier di rute ini", requested_intent="analytics")

    response = service.handle(request)

    assert response.intent == "analytics"
    assert response.route == ["intent", "graph", "synthesis"]
    assert response.abstained is False
    assert response.answer_available is True
    assert response.requires_human_confirmation is False