"""E2E journey: OrchestrationService.stream() (jalur SSE internal) harus
mengeluarkan urutan event yang benar -- meta, status, citation* (kalau ada),
lalu done -- dengan correlation_id konsisten di seluruh event.
"""

from tests.e2e._support import build_service, make_request, regulation_retrieve


def test_sse_stream_emits_meta_status_citation_then_done_in_order() -> None:
    service = build_service(retrieve_func=regulation_retrieve)
    request = make_request(query="regulation", requested_intent="regulation")

    events = list(service.stream(request))
    event_types = [event["event"] for event in events]

    assert event_types[0] == "meta"
    assert event_types[1] == "status"
    assert event_types[-1] == "done"
    assert event_types.count("citation") == 1  # regulation_retrieve returns exactly one citation


def test_sse_stream_correlation_id_is_consistent_across_all_events() -> None:
    service = build_service(retrieve_func=regulation_retrieve)
    request = make_request(query="regulation", requested_intent="regulation")

    events = list(service.stream(request))
    correlation_ids = {event["correlation_id"] for event in events}

    assert len(correlation_ids) == 1
    assert correlation_ids == {str(request.correlation_id)}


def test_sse_done_event_payload_matches_handle_response() -> None:
    service = build_service(retrieve_func=regulation_retrieve)
    request = make_request(query="regulation", requested_intent="regulation")

    events = list(service.stream(request))
    done_event = events[-1]

    assert done_event["event"] == "done"
    assert done_event["data"]["abstained"] is False
    assert done_event["data"]["answer_available"] is True
    assert len(done_event["data"]["citations"]) == 1