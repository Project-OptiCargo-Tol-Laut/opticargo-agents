"""Evaluasi: pastikan OrchestrationResponse ASLI yang dihasilkan pipeline
matching selalu punya bentuk field yang lengkap dan konsisten (bukan
validasi dict buatan sendiri)."""

from tests.performance._support import build_service, make_request, successful_ml_response, voyage_graph_context

DATASET_VERSION = "1.0.0"
THRESHOLD = 1.0

REQUIRED_FIELDS = {
    "correlation_id",
    "intent",
    "route",
    "answer",
    "answer_available",
    "abstained",
    "abstention_reason",
    "citations",
    "requires_human_confirmation",
    "trace",
}

DATASET = [
    {
        "name": "matching_dengan_kandidat_valid",
        "graph_context": voyage_graph_context(),
        "ml_response": successful_ml_response(),
    },
    {
        "name": "matching_tanpa_kandidat",
        "graph_context": voyage_graph_context(candidates=[]),
        "ml_response": successful_ml_response(),
    },
]


def test_recommendation_schema_quality() -> None:
    failures = []
    successes = 0

    for case in DATASET:
        service = build_service(
            graph_query_func=lambda *args, case=case, **kwargs: case["graph_context"],
            ml_response=case["ml_response"],
        )
        response = service.handle(make_request(query="carikan muatan dari makassar"))
        payload = response.to_dict()

        missing = REQUIRED_FIELDS - payload.keys()
        if missing:
            failures.append({"case": case["name"], "missing_fields": missing})
        else:
            successes += 1

    accuracy = successes / len(DATASET)

    assert accuracy >= THRESHOLD, (
        f"Recommendation schema quality {accuracy*100:.1f}% di bawah ambang {THRESHOLD*100:.1f}%. "
        f"Dataset Version: {DATASET_VERSION}. Failures: {failures}"
    )