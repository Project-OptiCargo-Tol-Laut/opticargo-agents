import pytest

# Dataset version 1.0.0
# Threshold: 80% accuracy minimum
DATASET_VERSION = "1.0.0"
THRESHOLD = 0.8

DATASET = [
    {"query": "aturan hukum terbaru kargo", "expected": "regulation"},
    {"query": "rekomendasi muatan dari makassar", "expected": "matching"},
    {"query": "rute perjalanan kapal ke papua", "expected": "route"},
    {"query": "ringkasan statistik", "expected": "analytics"},
    {"query": "hai apa kabar", "expected": "unknown"},
]

def test_intent_classification_dataset() -> None:
    from opticargo_agents.nodes.intent import run_intent_node

    failures = []
    successes = 0

    for item in DATASET:
        query = item["query"]
        expected = item["expected"]
        result = run_intent_node(query)
        if result.intent != expected:
            failures.append({"query": query, "expected": expected, "actual": result.intent})
        else:
            successes += 1

    accuracy = successes / len(DATASET)
    
    assert accuracy >= THRESHOLD, (
        f"Intent classification accuracy {accuracy*100:.1f}% is below threshold {THRESHOLD*100:.1f}%. "
        f"Dataset Version: {DATASET_VERSION}. Failures: {failures}"
    )
