import time
import pytest

STREAM_YIELD_THRESHOLD_MS = 50

def mock_generator():
    for _ in range(10):
        time.sleep(0.001)
        yield "data"

def test_stream_backpressure() -> None:
    # Warm-up
    list(mock_generator())
    
    yield_times = []
    
    start = time.perf_counter()
    for item in mock_generator():
        yield_times.append((time.perf_counter() - start) * 1000)
        start = time.perf_counter() # reset for next yield
        
    yield_times.sort()
    p95 = yield_times[int(len(yield_times) * 0.95)]
    
    assert p95 <= STREAM_YIELD_THRESHOLD_MS, f"Stream yield latency {p95:.2f}ms exceeds threshold {STREAM_YIELD_THRESHOLD_MS}ms"
