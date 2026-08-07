"""E2E journey: intent tidak dikenali -> Agents minta klarifikasi, tidak
mencoba menebak dan tidak memanggil dependency apapun (route pendek:
intent -> synthesis saja).
"""

from tests.e2e._support import build_service, make_request


def test_unknown_intent_asks_for_clarification_without_calling_dependencies() -> None:
    service = build_service()  # no adapters wired: must not be called at all
    request = make_request(query="asdkjaslkdj random gibberish text")

    response = service.handle(request)

    assert response.intent == "unknown"
    assert response.route == ["intent", "synthesis"]
    assert response.abstained is True
    assert response.answer_available is False
    assert response.answer is not None  # clarification message is user-facing text
    assert response.requires_human_confirmation is False