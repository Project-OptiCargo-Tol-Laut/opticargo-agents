import time
import pytest

ML_BATCH_LATENCY_THRESHOLD_MS = 800

def mock_batch_scoring(batch_size):
    time.sleep(0.002 * batch_size)

def test_ml_scoring_batch() -> None:
    # Warm-up
    mock_batch_scoring(5)
    
    latencies = []
    sample_size = 20
    batch_size = 100
    
    for _ in range(sample_size):
        start = time.perf_counter()
        mock_batch_scoring(batch_size)
        latencies.append((time.perf_counter() - start) * 1000)
        
    latencies.sort()
    p95 = latencies[int(sample_size * 0.95)]
    
    assert p95 <= ML_BATCH_LATENCY_THRESHOLD_MS, f"ML scoring batch latency {p95:.2f}ms exceeds threshold {ML_BATCH_LATENCY_THRESHOLD_MS}ms"
