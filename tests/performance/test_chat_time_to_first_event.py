import time

from tests.performance._support import build_service, make_request, regulation_retrieve

TTFE_THRESHOLD_MS = 100


def test_chat_time_to_first_event() -> None:
    """Ukur Time-To-First-Event (TTFE) dari OrchestrationService.stream() asli --
    seberapa cepat event 'meta' pertama sampai ke client setelah request masuk."""
    service = build_service(retrieve_func=regulation_retrieve)

    for _ in range(2):
        list(service.stream(make_request(query="aturan kirim kopra")))

    latencies = []
    sample_size = 20
    for _ in range(sample_size):
        start = time.perf_counter()
        stream = service.stream(make_request(query="aturan kirim kopra"))
        first_event = next(stream)
        latencies.append((time.perf_counter() - start) * 1000)
        list(stream)  # habiskan sisa event

    assert first_event["event"] == "meta"

    latencies.sort()
    p95 = latencies[int(sample_size * 0.95)]

    assert p95 <= TTFE_THRESHOLD_MS, f"p95 TTFE {p95:.2f}ms melebihi ambang {TTFE_THRESHOLD_MS}ms"