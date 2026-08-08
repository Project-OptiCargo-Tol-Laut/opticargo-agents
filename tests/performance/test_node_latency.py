import time

from opticargo_agents.nodes.intent import run_intent_node

NODE_LATENCY_P99_THRESHOLD_MS = 50


def test_node_latency() -> None:
    """Ukur latensi node murni (tanpa I/O) yang sesungguhnya: run_intent_node."""
    queries = [
        "aturan kirim kopra dari ternate",
        "carikan muatan dari surabaya ke makassar",
        "rute kapal dari sorong ke ambon",
        "ringkasan statistik voyage bulan ini",
        "halo apa kabar",
    ]

    for query in queries:
        run_intent_node(query)  # warm-up

    latencies = []
    sample_size = 100
    for i in range(sample_size):
        query = queries[i % len(queries)]
        start = time.perf_counter()
        run_intent_node(query)
        latencies.append((time.perf_counter() - start) * 1000)

    latencies.sort()
    p99 = latencies[int(sample_size * 0.99)]

    assert p99 <= NODE_LATENCY_P99_THRESHOLD_MS, (
        f"p99 latensi run_intent_node {p99:.2f}ms melebihi ambang {NODE_LATENCY_P99_THRESHOLD_MS}ms"
    )