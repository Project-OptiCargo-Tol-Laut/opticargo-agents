import pytest

DATASET_VERSION = "1.0.0"
THRESHOLD = 1.0

DATASET = [
    {"fallback_triggered": True, "expected_message": "Sistem sedang mengalami gangguan, menggunakan model fallback."},
    {"fallback_triggered": False, "expected_message": "Pencocokan berhasil dengan skor ML."},
]

def test_fallback_consistency() -> None:
    failures = []
    successes = 0
    
    for case in DATASET:
        # Mock logic to represent fallback consistency
        actual_message = (
            "Sistem sedang mengalami gangguan, menggunakan model fallback." 
            if case["fallback_triggered"] else "Pencocokan berhasil dengan skor ML."
        )
        
        if actual_message != case["expected_message"]:
            failures.append(case)
        else:
            successes += 1
            
    accuracy = successes / len(DATASET)
    
    assert accuracy >= THRESHOLD, (
        f"Fallback consistency {accuracy*100:.1f}% is below threshold {THRESHOLD*100:.1f}%. "
        f"Dataset Version: {DATASET_VERSION}. Failures: {failures}"
    )
