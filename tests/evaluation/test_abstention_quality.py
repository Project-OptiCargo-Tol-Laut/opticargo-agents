import pytest

DATASET_VERSION = "1.0.0"
THRESHOLD = 1.0

DATASET = [
    {"query": "tidak relevan", "should_abstain": True},
    {"query": "butuh rute dari makassar", "should_abstain": False},
]

def test_abstention_quality() -> None:
    from opticargo_agents.nodes.intent import run_intent_node
    
    failures = []
    successes = 0
    
    for case in DATASET:
        intent = run_intent_node(case["query"])
        # If intent is unknown, it will eventually lead to abstention for clarification
        is_abstained = intent.intent == "unknown"
        if is_abstained != case["should_abstain"]:
            failures.append(case)
        else:
            successes += 1
            
    accuracy = successes / len(DATASET)
    
    assert accuracy >= THRESHOLD, (
        f"Abstention quality accuracy {accuracy*100:.1f}% is below threshold {THRESHOLD*100:.1f}%. "
        f"Dataset Version: {DATASET_VERSION}. Failures: {failures}"
    )
