import time
import pytest

NODE_LATENCY_THRESHOLD_MS = 100

def mock_node_execution():
    time.sleep(0.001)

def test_node_latency() -> None:
    # Warm-up
    for _ in range(5):
        mock_node_execution()
        
    latencies = []
    sample_size = 100
    
    for _ in range(sample_size):
        start = time.perf_counter()
        mock_node_execution()
        latencies.append((time.perf_counter() - start) * 1000)
        
    latencies.sort()
    p99 = latencies[int(sample_size * 0.99)]
    
    assert p99 <= NODE_LATENCY_THRESHOLD_MS, f"p99 Node Latency {p99:.2f}ms exceeds threshold {NODE_LATENCY_THRESHOLD_MS}ms"
