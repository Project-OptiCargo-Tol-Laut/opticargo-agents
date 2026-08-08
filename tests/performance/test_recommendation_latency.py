import time

from tests.performance._support import (
    build_service,
    make_request,
    successful_ml_response,
    voyage_graph_context,
)

P95_THRESHOLD_MS = 200


def test_recommendation_latency() -> None:
    """Ukur latensi end-to-end pipeline matching (intent->graph->optimization->
    retrieval->synthesis) yang sesungguhnya, dengan dependency palsu yang cepat
    (bukan Neo4j/Qdrant/ML asli) -- yang diukur adalah overhead kode kita sendiri."""
    context = voyage_graph_context()
    service = build_service(
        graph_query_func=lambda *args, **kwargs: context,
        ml_response=successful_ml_response(),
    )

    for _ in range(3):
        service.handle(make_request(query="carikan muatan dari makassar"))

    latencies = []
    sample_size = 50
    for _ in range(sample_size):
        start = time.perf_counter()
        response = service.handle(make_request(query="carikan muatan dari makassar"))
        latencies.append((time.perf_counter() - start) * 1000)

    assert response.answer_available is True

    latencies.sort()
    p50 = latencies[int(sample_size * 0.50)]
    p95 = latencies[int(sample_size * 0.95)]

    assert p95 <= P95_THRESHOLD_MS, (
        f"p95 latensi pipeline matching {p95:.2f}ms (p50={p50:.2f}ms) melebihi ambang {P95_THRESHOLD_MS}ms"
    )