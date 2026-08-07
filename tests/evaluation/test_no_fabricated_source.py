import pytest

DATASET_VERSION = "1.0.0"
THRESHOLD = 1.0

DATASET = [
    {"response": "Berdasarkan dokumen A...", "citations": ["A"], "has_hallucination": False},
    {"response": "Berdasarkan dokumen B...", "citations": [], "has_hallucination": True},
]

def test_no_fabricated_source() -> None:
    failures = []
    successes = 0
    
    for case in DATASET:
        # Simple heuristic for evaluation dataset mock
        citations_found = len(case["citations"]) > 0
        claims_source = "berdasarkan" in case["response"].lower()
        
        is_hallucinating = claims_source and not citations_found
        
        if is_hallucinating != case["has_hallucination"]:
            failures.append(case)
        else:
            successes += 1
            
    accuracy = successes / len(DATASET)
    
    assert accuracy >= THRESHOLD, (
        f"No fabricated source quality {accuracy*100:.1f}% is below threshold {THRESHOLD*100:.1f}%. "
        f"Dataset Version: {DATASET_VERSION}. Failures: {failures}"
    )
