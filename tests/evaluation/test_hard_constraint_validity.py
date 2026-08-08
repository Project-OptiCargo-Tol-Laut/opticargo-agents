"""Evaluasi: pastikan run_cargo_scoring_node ASLI mengecualikan kandidat yang
melanggar hard constraint dari ranking, bukan mock logic terpisah."""

from opticargo_agents.clients import MLModelsClient
from opticargo_agents.config import load_settings
from opticargo_agents.nodes.optimization import run_cargo_scoring_node

DATASET_VERSION = "1.0.0"
THRESHOLD = 1.0


class _FakeTransport:
    def __init__(self, response):
        self.response = response

    def post_json(self, url, payload, headers, timeout):
        return self.response


DATASET = [
    {
        "name": "constraint_valid",
        "ml_response": {"score": 0.72, "hard_constraint_valid": True, "fallback_used": False},
        "expect_usable": True,
    },
    {
        "name": "constraint_invalid_meski_skor_tinggi",
        "ml_response": {"score": 0.95, "hard_constraint_valid": False, "fallback_used": False},
        "expect_usable": False,
    },
]


def test_hard_constraint_validity() -> None:
    failures = []
    successes = 0

    for case in DATASET:
        settings = load_settings({"ML_MODELS_INTERNAL_URL": "http://ml-models"})
        client = MLModelsClient(settings, transport=_FakeTransport(case["ml_response"]))
        result = run_cargo_scoring_node({"voyage": {}, "candidate": {}}, client)

        if result.available != case["expect_usable"]:
            failures.append({"case": case["name"], "available": result.available, "error": result.error})
        else:
            successes += 1

    accuracy = successes / len(DATASET)

    assert accuracy >= THRESHOLD, (
        f"Hard constraint validity {accuracy*100:.1f}% di bawah ambang {THRESHOLD*100:.1f}%. "
        f"Dataset Version: {DATASET_VERSION}. Failures: {failures}"
    )