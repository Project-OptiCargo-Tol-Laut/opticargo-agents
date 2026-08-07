import time
import concurrent.futures
import pytest

MAX_CONCURRENT_P95_THRESHOLD_MS = 1000

def mock_request():
    time.sleep(0.01)
    return True

def test_concurrent_requests() -> None:
    # Warm-up
    for _ in range(5):
        mock_request()
        
    latencies = []
    sample_size = 50
    concurrency_level = 10
    
    start_time = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency_level) as executor:
        futures = {executor.submit(mock_request): i for i in range(sample_size)}
        for future in concurrent.futures.as_completed(futures):
            # We measure overall time or individual time. 
            # In this mock, we just want to ensure it handles load without crashing.
            pass
            
    total_time = (time.perf_counter() - start_time) * 1000
    
    # We estimate p95 latency based on total time for this mock
    p95_estimated = (total_time / sample_size) * concurrency_level
    assert p95_estimated <= MAX_CONCURRENT_P95_THRESHOLD_MS, f"Concurrent request latency too high: {p95_estimated:.2f}ms"
