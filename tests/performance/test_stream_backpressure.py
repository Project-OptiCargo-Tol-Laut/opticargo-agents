import time

from tests.performance._support import build_service, make_request, regulation_retrieve

STREAM_YIELD_P95_THRESHOLD_MS = 50


def test_stream_backpressure() -> None:
    """Ukur jeda antar-event pada OrchestrationService.stream() asli -- pastikan
    tidak ada satupun event yang tertahan lama (indikasi backpressure/node hang)."""
    service = build_service(retrieve_func=regulation_retrieve)

    list(service.stream(make_request(query="aturan kirim kopra")))  # warm-up

    yield_gaps_ms = []
    start = time.perf_counter()
    for _ in service.stream(make_request(query="aturan kirim kopra")):
        now = time.perf_counter()
        yield_gaps_ms.append((now - start) * 1000)
        start = now

    assert yield_gaps_ms, "Stream tidak menghasilkan event apapun"

    yield_gaps_ms.sort()
    p95 = yield_gaps_ms[int(len(yield_gaps_ms) * 0.95)]

    assert p95 <= STREAM_YIELD_P95_THRESHOLD_MS, (
        f"p95 jeda antar-event {p95:.2f}ms melebihi ambang {STREAM_YIELD_P95_THRESHOLD_MS}ms"
    )