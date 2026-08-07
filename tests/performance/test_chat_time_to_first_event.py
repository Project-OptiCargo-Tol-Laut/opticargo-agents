import time
import pytest

# Time To First Event threshold
TTFE_THRESHOLD_MS = 200

def mock_chat_stream():
    # Simulates chat stream yielding first event
    time.sleep(0.005)
    yield "data: first event\n\n"
    time.sleep(0.01)
    yield "data: [DONE]\n\n"

def test_chat_time_to_first_event() -> None:
    # Warm-up
    for _ in range(2):
        list(mock_chat_stream())
        
    latencies = []
    sample_size = 20
    
    for _ in range(sample_size):
        start = time.perf_counter()
        stream = mock_chat_stream()
        next(stream) # Get first event
        latencies.append((time.perf_counter() - start) * 1000)
        list(stream) # Consume rest
        
    latencies.sort()
    p95 = latencies[int(sample_size * 0.95)]
    
    assert p95 <= TTFE_THRESHOLD_MS, f"p95 TTFE {p95:.2f}ms exceeds threshold {TTFE_THRESHOLD_MS}ms"
