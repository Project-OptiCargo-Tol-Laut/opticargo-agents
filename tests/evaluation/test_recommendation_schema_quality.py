import pytest

DATASET_VERSION = "1.0.0"
THRESHOLD = 1.0

DATASET = [
    {"payload": {"score": 0.8, "valid": True}, "is_valid_expected": True},
    {"payload": {"score": 0.8}, "is_valid_expected": False},
]

def test_recommendation_schema_quality() -> None:
    failures = []
    successes = 0
    
    for case in DATASET:
        is_valid = True
        payload = case["payload"]
        if "score" not in payload or "valid" not in payload:
            is_valid = False
        elif not isinstance(payload["score"], (int, float)):
            is_valid = False
        elif not isinstance(payload["valid"], bool):
            is_valid = False
            
        if is_valid != case["is_valid_expected"]:
            failures.append(case)
        else:
            successes += 1
            
    accuracy = successes / len(DATASET)
    
    assert accuracy >= THRESHOLD, (
        f"Recommendation schema quality {accuracy*100:.1f}% is below threshold {THRESHOLD*100:.1f}%. "
        f"Dataset Version: {DATASET_VERSION}. Failures: {failures}"
    )
