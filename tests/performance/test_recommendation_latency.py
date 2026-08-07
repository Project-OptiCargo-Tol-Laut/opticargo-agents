import time
import pytest

# Threshold for latency
P95_THRESHOLD_MS = 500

def mock_recommendation_pipeline():
    # Simulates the latency of the recommendation pipeline
    time.sleep(0.01)
    return True

def test_recommendation_latency() -> None:
    # Warm-up
    for _ in range(2):
        mock_recommendation_pipeline()
        
    latencies = []
    sample_size = 50
    
    for _ in range(sample_size):
        start = time.perf_counter()
        mock_recommendation_pipeline()
        latencies.append((time.perf_counter() - start) * 1000)
        
    latencies.sort()
    p50 = latencies[int(sample_size * 0.50)]
    p95 = latencies[int(sample_size * 0.95)]
    p99 = latencies[int(sample_size * 0.99)]
    
    # Check threshold
    assert p95 <= P95_THRESHOLD_MS, f"p95 latency {p95:.2f}ms exceeds threshold {P95_THRESHOLD_MS}ms"
