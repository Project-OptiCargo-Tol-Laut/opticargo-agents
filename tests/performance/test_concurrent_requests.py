import concurrent.futures
import time

from tests.performance._support import build_service, make_request, successful_ml_response, voyage_graph_context

MAX_CONCURRENT_P95_THRESHOLD_MS = 500


def test_concurrent_requests() -> None:
    """Ukur perilaku OrchestrationService.handle() asli di bawah beban konkuren,
    termasuk semaphore concurrency limit -- pastikan sistem tetap menangani beban
    tanpa deadlock/error, dan latensi tidak meledak."""
    context = voyage_graph_context()
    service = build_service(
        graph_query_func=lambda *args, **kwargs: context,
        ml_response=successful_ml_response(),
    )

    def call_once() -> float:
        start = time.perf_counter()
        response = service.handle(make_request(query="carikan muatan dari makassar"))
        assert response.answer_available is True
        return (time.perf_counter() - start) * 1000

    sample_size = 30
    concurrency_level = 8

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency_level) as executor:
        futures = [executor.submit(call_once) for _ in range(sample_size)]
        latencies = [f.result() for f in concurrent.futures.as_completed(futures)]

    latencies.sort()
    p95 = latencies[int(sample_size * 0.95)]

    assert p95 <= MAX_CONCURRENT_P95_THRESHOLD_MS, (
        f"p95 latensi di bawah beban konkuren {p95:.2f}ms melebihi ambang {MAX_CONCURRENT_P95_THRESHOLD_MS}ms"
    )