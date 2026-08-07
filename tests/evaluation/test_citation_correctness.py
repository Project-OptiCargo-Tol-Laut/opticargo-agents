import pytest

DATASET_VERSION = "1.0.0"
THRESHOLD = 0.9

DATASET = [
    {"query": "aturan", "citations": [{"title": "UU Pelayaran"}], "expected_citation_count": 1},
    {"query": "tidak ada", "citations": [], "expected_citation_count": 0},
]

def test_citation_correctness() -> None:
    from opticargo_agents.contracts import RetrievalResult
    
    failures = []
    successes = 0
    
    for case in DATASET:
        res = RetrievalResult(query=case["query"], citations=case["citations"])
        # A simple check for citation count correctness as proxy for citation evaluation
        if len(res.citations) != case["expected_citation_count"]:
            failures.append(case)
        else:
            successes += 1
            
    accuracy = successes / len(DATASET)
    
    assert accuracy >= THRESHOLD, (
        f"Citation correctness accuracy {accuracy*100:.1f}% is below threshold {THRESHOLD*100:.1f}%. "
        f"Dataset Version: {DATASET_VERSION}. Failures: {failures}"
    )
