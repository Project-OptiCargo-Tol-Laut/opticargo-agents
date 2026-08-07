"""E2E journey: route intent -> graph -> retrieval -> synthesis. Menjawab
info voyage/rute tanpa memerlukan confirmation manusia (bukan rekomendasi
transaksional).
"""

from tests.e2e._support import build_service, make_request, voyage_graph_context


def test_route_chat_describes_active_leg_from_graph_context() -> None:
    service = build_service(graph_query_func=lambda session, **kwargs: voyage_graph_context())
    request = make_request(query="rute voyage ini kemana", requested_intent="route")

    response = service.handle(request)

    assert response.intent == "route"
    assert response.route == ["intent", "graph", "retrieval", "synthesis"]
    assert response.abstained is False
    assert "Sorong" in (response.answer or "") or "Makassar" in (response.answer or "")
    assert response.requires_human_confirmation is False