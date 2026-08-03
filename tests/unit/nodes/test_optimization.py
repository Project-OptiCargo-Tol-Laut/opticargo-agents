from opticargo_agents.clients import MLModelsClient
from opticargo_agents.config import load_settings
from opticargo_agents.nodes.optimization import run_cargo_scoring_node


class FakeTransport:
    def __init__(self, response):
        self.response = response

    def post_json(self, url, payload, headers, timeout):
        return self.response


def _client(response) -> MLModelsClient:
    settings = load_settings({"ML_MODELS_INTERNAL_URL": "http://ml-models:8000"})
    return MLModelsClient(settings, transport=FakeTransport(response))


def test_optimization_node_returns_score_when_hard_constraint_valid() -> None:
    client = _client(
        {
            "score": 0.72,
            "model_mode": "heuristic",
            "hard_constraint_valid": True,
            "fallback_used": False,
            "warnings": [],
        }
    )

    result = run_cargo_scoring_node({"voyage": {}, "candidate": {}}, client)

    assert result.available is True
    assert result.score == 0.72


def test_optimization_node_excludes_candidate_when_hard_constraint_invalid() -> None:
    client = _client(
        {
            "score": 0.95,
            "model_mode": "heuristic",
            "hard_constraint_valid": False,
            "fallback_used": False,
            "warnings": [],
        }
    )

    result = run_cargo_scoring_node({"voyage": {}, "candidate": {}}, client)

    assert result.available is False
    assert result.error is not None
    assert result.error.code == "hard_constraint_violation"


def test_optimization_node_propagates_dependency_error_unchanged() -> None:
    client = MLModelsClient(load_settings({}), transport=FakeTransport({}))

    result = run_cargo_scoring_node({}, client)

    assert result.available is False
    assert result.fallback_used is True
    assert result.error.dependency == "ml_models"